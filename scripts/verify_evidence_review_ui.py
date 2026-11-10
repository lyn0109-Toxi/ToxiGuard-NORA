"""Real Streamlit AppTest checks for source-review interactions (no live data)."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from streamlit.testing.v1 import AppTest
from nora.assertions import extract_assertions
from nora.evidence import extract_document
from nora.projects import ProjectBundle


def run():
    with tempfile.TemporaryDirectory(prefix='ntr-review-ui-') as tmp:
        os.environ['NORA_DATA_DIR'] = tmp
        for language, lang in [('한국어', 'ko'), ('English', 'en')]:
            p = ProjectBundle.new('Synthetic UI verification')
            first = extract_document(b'Model Name: First Model', 'same.txt', 'text/plain')
            second = extract_document(b'Model Name: Second Model', 'same.txt', 'text/plain')
            p.documents = [first, second]
            p.assertions = extract_assertions(second)
            for claim in p.assertions:
                claim.review_status = '승인'
            app = AppTest.from_file(str(ROOT / 'streamlit_app.py'), default_timeout=30)
            app.session_state['nora_project'] = p
            app.session_state['nora_language'] = language
            app.session_state['nav_page'] = 'assertions'
            app.run()
            assert not app.exception, app.exception
            assert app.button(key=f'apply_assert_{p.project_id}_{lang}').disabled
            app.radio(key='nav_page').set_value('documents').run()
            assert not app.exception, app.exception
            app.selectbox(key=f'selected_doc_id_{p.project_id}').set_value(second.document_id).run()
            app.selectbox(key=f'source_kind_{second.document_id}').set_value('customer_evidence').run()
            # Changing the control alone is not a saved classification.
            assert second.source_kind == 'unclassified'
            app.button(key=f'save_source_kind_{second.document_id}').click().run()
            assert second.source_kind == 'customer_evidence'
            assert first.source_kind == 'unclassified'
            # Repeated save remains safe and keeps the correct document selected.
            app.button(key=f'save_source_kind_{second.document_id}').click().run()
            app.radio(key='nav_page').set_value('assertions').run()
            assert not app.exception, app.exception
            assert not app.button(key=f'apply_assert_{p.project_id}_{lang}').disabled
            app.button(key=f'apply_assert_{p.project_id}_{lang}').click().run()
            assert not app.exception, app.exception
            assert p.assessment_input.ai_model.model_name == 'Second Model'
            assert app.session_state['nav_page'] == 'assessment'
            # Revisiting a classified source and marking it external blocks later application.
            app.radio(key='nav_page').set_value('documents').run()
            app.selectbox(key=f'selected_doc_id_{p.project_id}').set_value(second.document_id).run()
            app.selectbox(key=f'source_kind_{second.document_id}').set_value('external_reference').run()
            app.button(key=f'save_source_kind_{second.document_id}').click().run()
            app.radio(key='nav_page').set_value('assertions').run()
            assert not app.exception, app.exception
            assert app.button(key=f'apply_assert_{p.project_id}_{lang}').disabled
            print(f'PASS: {language}: same-name source selection, unsaved/saved classification, repeated save, application, return navigation, external blocking')

if __name__ == '__main__':
    run()
