from __future__ import annotations

import copy
import unittest
from nora.assertions import apply_reviewed_assertions, extract_assertions
from nora.evidence import DocumentRecord, extract_document
from nora.evidence_review import application_blockers, evidence_gap_rows, source_issues
from nora.models import AssessmentInput
from nora.projects import ProjectBundle


class EvidenceReviewTests(unittest.TestCase):
    def setUp(self):
        self.doc = extract_document(b'Model Name: Customer Model', 'model.txt', 'text/plain')
        self.assertions = extract_assertions(self.doc)
        self.claim = self.assertions[0]
        self.claim.review_status = '승인'

    def test_legacy_document_requires_classification(self):
        payload = self.doc.to_dict()
        payload.pop('source_kind')
        self.assertEqual(DocumentRecord.from_dict(payload).source_kind, 'unclassified')
        self.assertIn('source_unclassified', source_issues(self.claim, [self.doc]))

    def test_classification_persists_in_project_roundtrip(self):
        self.doc.source_kind = 'external_reference'
        project = ProjectBundle.new()
        project.documents = [self.doc]
        self.assertEqual(ProjectBundle.from_dict(project.to_dict()).documents[0].source_kind, 'external_reference')

    def test_source_gate_rejects_unclassified_external_and_missing(self):
        for kind in ('unclassified', 'external_reference', 'unexpected'):
            self.doc.source_kind = kind
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                apply_reviewed_assertions(AssessmentInput(), self.assertions, documents=[self.doc])
        with self.assertRaises(ValueError):
            apply_reviewed_assertions(AssessmentInput(), self.assertions, documents=[])

    def test_classified_reviewed_source_applies_without_mutating_input(self):
        self.doc.source_kind = 'customer_evidence'
        inp = AssessmentInput()
        updated = apply_reviewed_assertions(inp, iter(self.assertions), documents=iter([self.doc]))
        self.assertEqual(updated.ai_model.model_name, 'Customer Model')
        self.assertNotEqual(inp.ai_model.model_name, 'Customer Model')

    def test_source_integrity_and_ambiguity(self):
        self.doc.source_kind = 'customer_evidence'
        for attr, value in [('source_location', 'wrong page'), ('source_excerpt', 'invented evidence'), ('source_document_name', 'wrong.txt'), ('source_document_id', 'missing')]:
            claim = copy.deepcopy(self.claim)
            setattr(claim, attr, value)
            with self.subTest(attr=attr):
                self.assertTrue(source_issues(claim, [self.doc]))
        self.assertTrue(source_issues(self.claim, [self.doc, self.doc]))
        self.assertTrue(application_blockers([self.claim, self.claim], [self.doc]))

    def test_unreviewed_external_reference_is_not_applied(self):
        self.doc.source_kind = 'external_reference'
        self.claim.review_status = '제안됨'
        self.assertFalse(application_blockers(self.assertions, [self.doc]))
        updated = apply_reviewed_assertions(AssessmentInput(), self.assertions, documents=[self.doc])
        self.assertNotEqual(updated.ai_model.model_name, 'Customer Model')

    def test_gap_states_are_not_negative_findings(self):
        def state():
            return {r['field_path']: r['review_state'] for r in evidence_gap_rows(self.assertions, [self.doc])}
        self.assertEqual(state()['product.product_name'], 'not_extracted')
        self.assertEqual(state()['ai_model.model_name'], 'source_review_required')
        self.doc.source_kind = 'customer_evidence'
        self.assertEqual(state()['ai_model.model_name'], 'reviewed_source_linked')
        self.claim.review_status = '제안됨'
        self.assertEqual(state()['ai_model.model_name'], 'human_review_pending')
        self.claim.review_status = '거절'
        self.assertEqual(state()['ai_model.model_name'], 'all_candidates_rejected')

    def test_conflicts_remain_visible(self):
        second = copy.deepcopy(self.claim)
        second.assertion_id += '-2'
        second.proposed_value = 'Other Model'
        self.assertions.append(second)
        row = next(r for r in evidence_gap_rows(self.assertions, [self.doc]) if r['field_path'] == 'ai_model.model_name')
        self.assertEqual(row['review_state'], 'conflicting_reviewed_values')

    def test_blank_ids_and_ambiguous_locations_fail_closed(self):
        self.doc.source_kind = 'customer_evidence'
        self.doc.document_id = self.claim.source_document_id = ''
        self.assertTrue(source_issues(self.claim, [self.doc]))
        self.doc.document_id = self.claim.source_document_id = 'DOC-test'
        self.doc.segments.append(copy.deepcopy(self.doc.segments[0]))
        self.assertIn('source_excerpt_not_linked', source_issues(self.claim, [self.doc]))

    def test_invalid_hash_metadata_and_empty_excerpt_are_blocked(self):
        self.doc.source_kind = 'customer_evidence'
        self.doc.sha256 = 'not-a-hash'
        self.assertIn('source_metadata_mismatch', source_issues(self.claim, [self.doc]))
        self.claim.source_excerpt = '   '
        self.assertIn('source_excerpt_not_linked', source_issues(self.claim, [self.doc]))
