from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .evidence import EvidenceAssertion
from .models import AssessmentInput, AssessmentResult, DataGap, GateResult

LANGUAGE_NAMES = {"ko": "한국어", "en": "English"}

UI_TEXT: dict[str, dict[str, str]] = {
    "app_subtitle": {"ko": "AI·NAM 기반 초기 독성근거 검증", "en": "AI/NAM Early-Toxicity Evidence Assurance"},
    "header_description": {
        "ko": "AI와 비동물시험법(NAM)의 독성근거가 현재 후보물질의 개발에 어디까지 사용 가능한지 검증하는 Evidence Assurance 앱",
        "en": "An evidence-assurance application that evaluates how far AI and New Approach Methodology (NAM) toxicity evidence can be used for the current candidate.",
    },
    "tagline": {"ko": "시험을 대체하기 전에, 대체 근거부터 검증합니다.", "en": "Validate the evidence before replacing the experiment."},
    "header_principle": {
        "ko": "AI는 근거를 구조화하고, 규칙엔진은 근거 역할과 Data Gap을 분류하며, 동물시험 축소·대체와 같은 고영향 결론은 독성전문가가 검토합니다.",
        "en": "AI structures the evidence, the deterministic rule engine classifies evidence roles and data gaps, and toxicology experts review high-impact conclusions such as animal-study reduction or replacement.",
    },
    "language": {"ko": "언어", "en": "Language"},
    "prototype_note": {
        "ko": "연구·의사결정 지원용 프로토타입입니다. 제품 안전성, 동물시험 면제 또는 규제기관 수용을 보장하지 않습니다.",
        "en": "This is a research and decision-support prototype. It does not certify product safety, waive animal studies, or guarantee regulatory acceptance.",
    },
    "project": {"ko": "프로젝트", "en": "Project"},
    "documents": {"ko": "문서", "en": "Documents"},
    "assertions": {"ko": "Evidence Assertion", "en": "Evidence Assertions"},
    "approved_corrected": {"ko": "승인·수정", "en": "Approved / Corrected"},
    "current_role": {"ko": "현재 Evidence Role", "en": "Current Evidence Role"},
    "not_assessed": {"ko": "미평가", "en": "Not assessed"},
    "items_count": {"ko": "{count}개", "en": "{count}"},
    "workspace": {"ko": "작업공간", "en": "Workspace"},
    "project_management": {"ko": "프로젝트 관리", "en": "Project Management"},
    "project_name": {"ko": "프로젝트명", "en": "Project Name"},
    "project_owner": {"ko": "프로젝트 책임자", "en": "Project Owner"},
    "project_description": {"ko": "프로젝트 설명", "en": "Project Description"},
    "apply_metadata": {"ko": "메타데이터 반영", "en": "Apply Metadata"},
    "metadata_applied": {"ko": "프로젝트 정보를 반영했습니다.", "en": "Project metadata has been updated."},
    "new_project": {"ko": "새 프로젝트", "en": "New Project"},
    "local_save": {"ko": "로컬 저장", "en": "Save Locally"},
    "saved_local": {"ko": "SQLite 프로젝트 보관함에 저장했습니다.", "en": "Saved to the local SQLite project library."},
    "save_failed": {"ko": "저장 실패: {error}", "en": "Save failed: {error}"},
    "saved_projects": {"ko": "저장된 프로젝트", "en": "Saved Projects"},
    "none_selected": {"ko": "선택하지 않음", "en": "None selected"},
    "load": {"ko": "불러오기", "en": "Load"},
    "delete": {"ko": "삭제", "en": "Delete"},
    "deleted_local": {"ko": "로컬 보관함에서 삭제했습니다.", "en": "Deleted from the local project library."},
    "project_json_upload": {"ko": "프로젝트 JSON 불러오기", "en": "Import Project JSON"},
    "apply_json": {"ko": "JSON 프로젝트 적용", "en": "Apply JSON Project"},
    "project_json_error": {"ko": "프로젝트 JSON 오류: {error}", "en": "Project JSON error: {error}"},
    "download_project_json": {"ko": "현재 프로젝트 JSON", "en": "Current Project JSON"},
    "golden_case": {"ko": "Golden Case", "en": "Golden Case"},
    "synthetic_case": {"ko": "가상 사례", "en": "Synthetic Case"},
    "load_case": {"ko": "사례 불러오기", "en": "Load Case"},
    "project_overview": {"ko": "프로젝트 개요", "en": "Project Overview"},
    "consulting_studio": {"ko": "컨설팅 스튜디오", "en": "Advisory Studio"},
    "consulting_studio_title": {"ko": "고객 목적별 컨설팅 사례", "en": "Client-Objective Advisory Cases"},
    "consulting_studio_caption": {
        "ko": "고객 유형과 의사결정 목적에 맞는 사례를 비교하고, 현재 EarlyTox 엔진으로 평가할 수 있는 범위와 전문가 주도 범위를 구분합니다.",
        "en": "Compare cases by client segment and decision objective, and distinguish the current EarlyTox automation scope from expert-led advisory work.",
    },
    "next_best_action": {"ko": "다음 권장 작업", "en": "Next Best Action"},
    "case_filters": {"ko": "사례 필터", "en": "Case Filters"},
    "case_summary": {"ko": "선택 사례 요약", "en": "Selected Case Summary"},
    "case_deliverables": {"ko": "주요 산출물", "en": "Key Deliverables"},
    "case_actions": {"ko": "권장 다음 단계", "en": "Recommended Next Steps"},
    "case_library_table": {"ko": "사례 라이브러리", "en": "Case Library"},
    "document_evidence": {"ko": "문서 근거", "en": "Document Evidence"},
    "evidence_review": {"ko": "근거 검토", "en": "Evidence Review"},
    "assessment_input": {"ko": "평가 입력", "en": "Assessment Input"},
    "results_reports": {"ko": "결과·보고서", "en": "Results & Reports"},
    "rules_ontology": {"ko": "규칙·온톨로지", "en": "Rules & Ontology"},
    "overview_text": {
        "ko": "AI/NAM 독성근거를 단순 점수로 평가하지 않고, 방법·실행·후보 적용성·사람 관련성·노출 번역·근거 일치성을 분리해 검토합니다.",
        "en": "NORA does not reduce AI/NAM toxicity evidence to a single score. It separately reviews method credibility, execution validity, candidate applicability, human relevance, exposure translation, and evidence concordance.",
    },
    "current_question": {"ko": "현재 개발 질문", "en": "Current Development Question"},
    "qoi_missing": {"ko": "Question of Interest가 아직 정의되지 않았습니다. ‘평가 입력’에서 먼저 정의하십시오.", "en": "The Question of Interest has not yet been defined. Define it first under Assessment Input."},
    "item": {"ko": "항목", "en": "Item"},
    "current_value": {"ko": "현재 값", "en": "Current Value"},
    "assessment_objective": {"ko": "평가 목적", "en": "Assessment Objective"},
    "development_stage": {"ko": "개발 단계", "en": "Development Stage"},
    "target_endpoint": {"ko": "대상 Endpoint", "en": "Target Endpoint"},
    "intended_role": {"ko": "희망 Evidence Role", "en": "Intended Evidence Role"},
    "jurisdiction_context": {"ko": "관할·맥락", "en": "Jurisdiction / Context"},
    "product_context": {"ko": "제품 맥락", "en": "Product Context"},
    "candidate": {"ko": "후보물질", "en": "Candidate"},
    "target_mechanism": {"ko": "표적·기전", "en": "Target / Mechanism"},
    "carrier_formulation": {"ko": "전달체·제형", "en": "Carrier / Formulation"},
    "route_exposure": {"ko": "경로·노출", "en": "Route / Exposure"},
    "not_entered": {"ko": "미입력", "en": "Not entered"},
    "judgments_made": {"ko": "앱이 내리는 판단", "en": "What NORA Assesses"},
    "judgments_not_made": {"ko": "앱이 내리지 않는 판단", "en": "What NORA Does Not Decide"},
    "not_decide_text": {"ko": "안전성 인증 · 동물시험 면제 · 규제기관 승인 예측 · 전체 독성패키지 대체", "en": "Safety certification · animal-study waiver · regulatory approval prediction · replacement of the entire toxicology package"},
    "quick_start": {"ko": "빠른 시작", "en": "Quick Start"},
    "start_upload": {"ko": "문서 업로드로 시작", "en": "Start with Document Upload"},
    "start_manual": {"ko": "수동 평가 입력", "en": "Enter Assessment Manually"},
    "gplct_case": {"ko": "GP-L-CT 사례", "en": "GP-L-CT Case"},
    "document_workspace": {"ko": "문서 근거 작업공간", "en": "Document Evidence Workspace"},
    "document_workspace_caption": {
        "ko": "PDF, DOCX, TXT/MD, CSV, XLSX/XLSM, JSON을 업로드하면 페이지·문단·시트·행 위치를 보존한 근거 구간을 생성합니다. 스캔 PDF OCR은 현재 포함하지 않습니다.",
        "en": "Upload PDF, DOCX, TXT/MD, CSV, XLSX/XLSM, or JSON files to create evidence segments that preserve page, paragraph, sheet, and row locations. OCR for scanned PDFs is not included in this version.",
    },
    "document_uploader": {"ko": "AI 모델 카드, NAM 보고서, PK/TK, biodistribution 또는 기존 독성자료", "en": "AI model cards, NAM reports, PK/TK, biodistribution, or existing toxicology evidence"},
    "manual_evidence": {"ko": "직접 붙여넣을 근거 텍스트", "en": "Paste Evidence Text"},
    "manual_evidence_placeholder": {"ko": "모델 검증요약, NAM 결과, 대조군 및 노출정보 등을 붙여넣을 수 있습니다.", "en": "Paste model validation summaries, NAM results, control performance, exposure information, or related evidence."},
    "process_documents": {"ko": "선택 문서 처리", "en": "Process Selected Documents"},
    "processing_documents": {"ko": "문서를 구조화하고 Evidence Assertion 후보를 추출하는 중입니다...", "en": "Structuring documents and extracting candidate Evidence Assertions..."},
    "documents_added": {"ko": "문서 {added}개를 추가했습니다. 중복 {skipped}개는 제외했습니다.", "en": "Added {added} document(s). Skipped {skipped} duplicate(s)."},
    "add_pasted_text": {"ko": "붙여넣은 텍스트 추가", "en": "Add Pasted Text"},
    "manual_added": {"ko": "수동 근거 {added}개를 추가했습니다.", "en": "Added {added} manually entered evidence document(s)."},
    "no_documents": {"ko": "아직 업로드된 문서가 없습니다. 문서 없이 수동 입력만으로도 평가할 수 있지만, Evidence Role R4/R5에는 추적 가능한 근거가 중요합니다.", "en": "No documents have been uploaded. Manual assessment is possible, but traceable evidence is important for Evidence Roles R4 and R5."},
    "document_inventory": {"ko": "문서 인벤토리", "en": "Document Inventory"},
    "review_document": {"ko": "문서 검토", "en": "Review Document"},
    "evidence_segments": {"ko": "근거 구간", "en": "Evidence Segments"},
    "characters_extracted": {"ko": "추출 문자", "en": "Characters Extracted"},
    "auto_assertions": {"ko": "자동 Assertion", "en": "Auto-Extracted Assertions"},
    "warnings": {"ko": "경고", "en": "Warnings"},
    "document_warnings": {"ko": "문서 처리 경고", "en": "Document Processing Warnings"},
    "source_location": {"ko": "출처 위치", "en": "Source Location"},
    "extracted_text": {"ko": "추출 텍스트", "en": "Extracted Text"},
    "delete_document": {"ko": "이 문서 삭제", "en": "Delete This Document"},
    "delete_doc_note": {"ko": "문서를 삭제하면 해당 문서에서 생성된 Assertion도 함께 제거됩니다.", "en": "Deleting a document also removes Assertions generated from that document."},
    "assertion_review": {"ko": "Evidence Assertion 검토", "en": "Evidence Assertion Review"},
    "assertion_review_caption": {"ko": "자동 추출값은 모두 ‘제안됨’ 상태입니다. 평가 입력에 반영하려면 사람이 승인·수정·거절해야 합니다.", "en": "All automatically extracted values begin in Proposed status. A human must approve, correct, or reject them before they can affect the assessment input."},
    "no_assertions": {"ko": "검토할 Assertion이 없습니다. 먼저 문서를 업로드하거나 평가 입력을 수동으로 작성하십시오.", "en": "There are no Assertions to review. Upload documents first or complete the assessment input manually."},
    "total": {"ko": "전체", "en": "Total"},
    "proposed": {"ko": "제안됨", "en": "Proposed"},
    "approved": {"ko": "승인", "en": "Approved"},
    "corrected": {"ko": "수정", "en": "Corrected"},
    "rejected": {"ko": "거절", "en": "Rejected"},
    "category": {"ko": "분류", "en": "Category"},
    "review_status": {"ko": "검토 상태", "en": "Review Status"},
    "source_document": {"ko": "출처 문서", "en": "Source Document"},
    "search": {"ko": "검색", "en": "Search"},
    "search_placeholder": {"ko": "필드, 값, 발췌문 검색", "en": "Search field, value, or excerpt"},
    "no_filtered_assertions": {"ko": "현재 필터에 해당하는 Assertion이 없습니다.", "en": "No Assertions match the current filters."},
    "save_edits": {"ko": "편집 내용 저장", "en": "Save Edits"},
    "approve_filtered": {"ko": "필터 결과 모두 승인", "en": "Approve All Filtered"},
    "apply_approved": {"ko": "승인 근거를 평가 입력에 적용", "en": "Apply Reviewed Evidence to Assessment"},
    "review_saved": {"ko": "검토상태와 수정값을 저장했습니다.", "en": "Review statuses and corrected values have been saved."},
    "approved_applied": {"ko": "승인된 근거를 구조화된 평가 입력에 반영했습니다.", "en": "Reviewed evidence has been applied to the structured assessment input."},
    "evidence_principles": {"ko": "평가에 반영되는 근거 원칙", "en": "Evidence Inclusion Principles"},
    "structured_input": {"ko": "구조화된 평가 입력", "en": "Structured Assessment Input"},
    "structured_input_caption": {"ko": "승인된 Assertion을 자동 적용한 뒤 사람이 최종 입력값을 검토할 수 있습니다. 현재 상세 규칙의 활성 범위는 초기 간독성입니다.", "en": "Reviewed Assertions can be applied automatically, after which a human reviews the final structured inputs. The currently active detailed rule set is limited to early hepatotoxicity."},
    "save_assessment_input": {"ko": "평가 입력 저장", "en": "Save Assessment Input"},
    "assessment_saved": {"ko": "평가 입력을 저장했습니다.", "en": "Assessment input has been saved."},
    "results_title": {"ko": "NORA 자문 결과 및 보고서", "en": "NORA Advisory Results & Reports"},
    "results_caption": {"ko": "평가 결과는 안전성 인증이 아니라, 현재 근거의 사용 가능한 역할과 다음 근거를 설명합니다.", "en": "The assessment does not certify safety. It explains the current evidence role, its limits, and the next evidence needed."},
    "run_assessment": {"ko": "NORA EarlyTox 평가 실행", "en": "Run NORA EarlyTox Assessment"},
    "assessment_placeholder": {"ko": "평가를 실행하면 Evidence Role, Hard Gate, Data Gap, 자문 및 내보내기 파일이 생성됩니다.", "en": "Run the assessment to generate the Evidence Role, hard gates, data gaps, advisory interpretation, and export files."},
    "animal_recommendation": {"ko": "동물사용 관련 권고", "en": "Animal-Use Recommendation"},
    "model_risk": {"ko": "모델 위험", "en": "Model Risk"},
    "residual_uncertainty": {"ko": "잔여 불확실성", "en": "Residual Uncertainty"},
    "independent_streams": {"ko": "독립 근거 흐름", "en": "Independent Evidence Streams"},
    "assessment_dimensions": {"ko": "평가축", "en": "Assessment Dimensions"},
    "data_gap": {"ko": "Data Gap", "en": "Data Gaps"},
    "explainable_advisory": {"ko": "설명 가능한 자문", "en": "Explainable Advisory"},
    "evidence_ledger": {"ko": "Evidence Ledger", "en": "Evidence Ledger"},
    "audit_trail": {"ko": "Audit Trail", "en": "Audit Trail"},
    "impact": {"ko": "영향", "en": "Impact"},
    "no_major_gaps": {"ko": "자동 생성된 주요 Data Gap이 없습니다. 실제 사용 전 전문가 검토가 필요합니다.", "en": "No major Data Gaps were generated automatically. Expert review is still required before real-world use."},
    "observation": {"ko": "관찰", "en": "Observation"},
    "interpretation": {"ko": "해석", "en": "Interpretation"},
    "development_relevance": {"ko": "개발상 의미", "en": "Development Relevance"},
    "recommendations": {"ko": "권고사항", "en": "Recommendations"},
    "no_accepted_assertions": {"ko": "승인된 Evidence Assertion이 없습니다. 수동 입력으로 평가한 경우에도 R4/R5 전에는 근거 추적성을 보완하십시오.", "en": "No reviewed Evidence Assertions are available. Even for manually entered assessments, evidence traceability should be completed before R4 or R5 use."},
    "downloads": {"ko": "다운로드", "en": "Downloads"},
    "advisory_md": {"ko": "자문보고서(MD)", "en": "Advisory Report (MD)"},
    "advisory_pdf": {"ko": "자문보고서(PDF)", "en": "Advisory Report (PDF)"},
    "gap_csv": {"ko": "Data Gap CSV", "en": "Data Gap CSV"},
    "project_json": {"ko": "프로젝트 JSON", "en": "Project JSON"},
    "pdf_disabled": {"ko": "PDF 생성이 비활성화되었습니다: {error}", "en": "PDF generation is unavailable: {error}"},
    "rules_title": {"ko": "규칙 카탈로그와 TG-PTO-ET", "en": "Rule Catalog & TG-PTO-ET"},
    "rules_caption": {"ko": "OWL/RDF는 개념과 관계를 표현하고, SHACL은 필수정보와 추적성을 검증하며, 결정론적 Rule Engine이 Evidence Role과 Data Gap을 계산합니다.", "en": "OWL/RDF represents concepts and relationships, SHACL validates required information and traceability, and the deterministic Rule Engine calculates Evidence Roles and Data Gaps."},
    "rule_catalog": {"ko": "EarlyTox 규칙 카탈로그", "en": "EarlyTox Rule Catalog"},
    "top_constraints": {"ko": "최상위 논리제약", "en": "Top-Level Logical Constraints"},
}

PAGE_IDS = ["overview", "consulting", "documents", "assertions", "assessment", "results", "rules"]
PAGE_KEYS = {
    "overview": "project_overview",
    "consulting": "consulting_studio",
    "documents": "document_evidence",
    "assertions": "evidence_review",
    "assessment": "assessment_input",
    "results": "results_reports",
    "rules": "rules_ontology",
}

VALUE_EN: dict[str, str] = {
    # Context of Use
    "AI 독성예측 결과 검증": "Validate AI toxicity prediction",
    "NAM 결과의 사람 관련성 평가": "Assess human relevance of NAM results",
    "AI·NAM·기존 근거 통합": "Integrate AI, NAM, and existing evidence",
    "동물시험 범위 축소 가능성 평가": "Assess potential to reduce animal studies",
    "특정 독성시험 대체 후보 평가": "Assess candidate replacement for a specific toxicity study",
    "탐색 연구": "Discovery research",
    "후보물질 선정": "Candidate selection",
    "초기 비임상 개발": "Early nonclinical development",
    "IND/CTA 준비": "IND/CTA preparation",
    "초기 간독성": "Early hepatotoxicity",
    "신독성": "Nephrotoxicity",
    "심장독성": "Cardiotoxicity",
    "면역독성": "Immunotoxicity",
    "유전독성": "Genotoxicity",
    "R1 · 가설 생성": "R1 · Hypothesis generation",
    "R2 · 초기 선별": "R2 · Early screening",
    "R3 · 보조 근거": "R3 · Supportive evidence",
    "R4 · 동물시험 축소 지원": "R4 · Animal-study reduction support",
    "R5 · 특정 시험 대체 후보": "R5 · Candidate replacement for a specific study",
    "연구용 / 내부 의사결정": "Research / internal decision-making",
    "미국 FDA 사전미팅 준비": "US FDA pre-meeting preparation",
    "유럽 EMA Scientific Advice 준비": "EMA Scientific Advice preparation",
    "CTA/IND 근거 패키지 준비": "CTA/IND evidence-package preparation",
    # Product
    "저분자 NME": "Small-molecule NME",
    "올리고뉴클레오타이드": "Oligonucleotide therapeutic",
    "siRNA 치료제": "siRNA therapeutic",
    "나노의약품": "Nanomedicine",
    "siRNA + 나노의약품": "siRNA + nanomedicine",
    "바이오의약품": "Biologic",
    "유전자치료제": "Gene therapy",
    "경구": "Oral",
    "정맥투여": "Intravenous",
    "근육주사": "Intramuscular",
    "피하주사": "Subcutaneous",
    "흡입": "Inhalation",
    "국소": "Topical",
    "단회 노출": "Single exposure",
    "반복 노출": "Repeated exposure",
    "지속 노출": "Continuous exposure",
    "없음": "None",
    "정성적 자료": "Qualitative data",
    "정량적 자료": "Quantitative data",
    "불명확": "Unclear",
    "부분적으로 확인": "Partially confirmed",
    "임상제품 대표성 확인": "Clinical-product representativeness confirmed",
    # AI
    "음성 / 낮은 위험 예측": "Negative / low-risk prediction",
    "양성 / 위험 신호": "Positive / risk signal",
    "경계 / 불확실": "Borderline / uncertain",
    "저분자": "Small molecule",
    "검증됨": "Validated",
    "부분 검증": "Partially validated",
    "미검증": "Not validated",
    "확인됨": "Confirmed",
    "자동 평가": "Automatic assessment",
    "해당 없음": "Not applicable",
    # AI credibility v0.8
    "보정된 확률": "Calibrated probability",
    "정량 평가 — In-domain": "Quantitative assessment — In-domain",
    "정량 평가 — Borderline": "Quantitative assessment — Borderline",
    "정량 평가 — Out-of-domain": "Quantitative assessment — Out-of-domain",
    "기전과 연결됨": "Linked to a plausible toxicity mechanism",
    "부분 연결": "Partially linked to mechanism",
    "원시 모델점수": "Raw model score",
    "Ensemble agreement": "Ensemble agreement",
    "전문가 adjudication / 임상 기준": "Expert-adjudicated / clinical reference standard",
    "검증된 in vivo / 병리 기준": "Validated in vivo / pathology reference standard",
    "검증된 NAM 기준": "Validated NAM reference standard",
    "문헌 / 라벨 기반": "Literature / label-derived reference",
    "전문가 검토·합의": "Expert review and consensus",
    "독립적 검토": "Independent review",
    "단일 출처 / 자동 라벨": "Single-source / automated label",
    "미평가와 음성을 명확히 구분": "Untested/missing clearly separated from negative",
    "일부 구분": "Partially distinguished",
    "미평가를 음성으로 처리": "Untested/missing treated as negative",
    "외부 독립검증": "Independent external validation",
    "시간 분할": "Temporal split",
    "Scaffold 분할": "Scaffold split",
    "무작위 분할": "Random split",
    "독립 확인": "Independence confirmed",
    "비독립 / 중복 확인": "Non-independent / overlap confirmed",
    "평가 완료 — 문제 없음": "Assessed — no issue identified",
    "누수 가능성": "Possible leakage",
    "누수 확인": "Leakage confirmed",
    "미평가": "Not assessed",
    "중복 제거 / 관리": "Duplicates removed / controlled",
    "중복 확인": "Duplicates identified",
    "현재 COU에 적절": "Representative for the current COU",
    "부분적으로 적절": "Partially representative",
    "현재 COU에 부적절": "Not representative for the current COU",
    "부적절": "Inadequate",
    "보고됨": "Reported",
    "부분 보고": "Partially reported",
    "정량적 OOD 평가 있음": "Quantitative OOD assessment available",
    "계획 있음": "Planned",
    "운영 중": "Operational",
    "정의됨": "Defined",
    "부분 정의": "Partially defined",
    "검증된 feature attribution": "Validated feature attribution",
    "낮음–중간": "Low to moderate",
    "중간–높음": "Moderate to high",
    # NAM
    "2D 세포시험": "2D cell assay",
    "공배양(Coculture)": "Coculture",
    "3D 간 Spheroid": "3D liver spheroid",
    "간 Organoid": "Liver organoid",
    "Omics 기반 시험": "Omics-based assay",
    "사람 유래": "Human-derived",
    "사람·동물 혼합": "Mixed human/animal",
    "동물 유래": "Animal-derived",
    "음성": "Negative",
    "양성": "Positive",
    "경계": "Equivocal",
    "시험 무효": "Invalid study execution",
    "간세포(Hepatocyte)": "Hepatocyte",
    "간 내피세포": "Liver sinusoidal endothelial cell",
    "담관세포": "Cholangiocyte",
    "충분히 확인": "Adequately characterized",
    "부분 확인": "Partially characterized",
    "확인되지 않음": "Not characterized",
    "충분": "Adequate",
    "부분적": "Partial",
    "미포함 / 불명확": "Not included / unclear",
    "단회/급성 노출": "Single / acute exposure",
    "반복노출": "Repeated exposure",
    "지속노출": "Continuous exposure",
    "유효": "Valid",
    "실패": "Failed",
    "없음 / 불명확": "Missing / unclear",
    "포함": "Included",
    "미포함": "Not included",
    "완결": "Complete",
    "불충분": "Insufficient",
    "측정됨": "Measured",
    "부분 측정": "Partially measured",
    "측정 안 됨": "Not measured",
    "수행됨": "Performed",
    "초기 연결": "Preliminary linkage",
    "Donor/lot/반복 재현성 확인": "Donor/lot/repeat reproducibility confirmed",
    "일부 확인": "Partially confirmed",
    "미토콘드리아 기능": "Mitochondrial function",
    "산화스트레스": "Oxidative stress",
    "담즙산 수송": "Bile-acid transport",
    "CYP 대사기능": "CYP metabolic function",
    # Review
    "제안됨": "Proposed",
    "승인": "Approved",
    "수정": "Corrected",
    "거절": "Rejected",
    "전체": "All",
    # Status / severity
    "통과": "Pass",
    "미통과": "Fail",
    "조건부": "Conditional",
    "결정 제한": "Decision-limiting",
    "주요 보완": "Major gap",
    "낮음": "Low",
    "중간": "Moderate",
    "높음": "High",
    "매우 높음": "Very high",
}

CASE_EN = {
    "GP-L-CT — 적용범위 밖 음성예측": "GP-L-CT — Out-of-domain negative prediction",
    "저분자 — 일치하는 고품질 근거": "Small molecule — Concordant high-quality evidence",
    "저분자 — AI/NAM 상충": "Small molecule — Conflicting AI/NAM evidence",
}

CATEGORY_EN = {
    "제품": "Product",
    "AI 모델": "AI Model",
    "NAM 시험": "NAM Assay",
    "노출": "Exposure",
    "보조 근거": "Supporting Evidence",
}

FIELD_PATH_EN = {
    "product.product_name": "Candidate name",
    "product.active_substance": "Active substance / sequence",
    "product.target_mechanism": "Target / mechanism",
    "product.carrier_formulation": "Carrier / formulation",
    "product.modality": "Product modality",
    "product.route": "Route of administration",
    "product.exposure_pattern": "Planned exposure pattern",
    "product.distribution_status": "Biodistribution status",
    "ai_model.model_name": "AI model name",
    "ai_model.model_version": "AI model version",
    "ai_model.sensitivity_percent": "Sensitivity",
    "ai_model.specificity_percent": "Specificity",
    "ai_model.false_negative_rate_percent": "False-negative rate",
    "ai_model.external_validation": "External validation",
    "ai_model.calibration_status": "Calibration",
    "ai_model.endpoint": "AI prediction endpoint",
    "ai_model.result": "AI prediction result",
    "ai_model.domain_modalities": "AI training modality",
    "nam_assay.nam_type": "NAM type",
    "nam_assay.system_origin": "Test-system origin",
    "nam_assay.cell_types": "Included cell types",
    "nam_assay.result": "NAM result",
    "nam_assay.positive_control": "Positive control",
    "nam_assay.negative_control": "Negative control",
    "nam_assay.carrier_only_control": "Carrier-only control",
    "nam_assay.measured_exposure": "Measured exposure",
    "nam_assay.qivive_pbpk": "QIVIVE/PBPK",
    "nam_assay.exposure_design": "NAM exposure design",
    "nam_assay.metabolic_competence": "Metabolic competence",
    "nam_assay.reproducibility": "Reproducibility",
    "nam_assay.endpoints": "NAM endpoint",
    "supporting_evidence.mechanistic_evidence": "Mechanistic evidence",
    "supporting_evidence.class_or_clinical_evidence": "Class / clinical evidence",
    "supporting_evidence.quantitative_biodistribution": "Quantitative biodistribution",
    "supporting_evidence.pk_tk_evidence": "PK/TK evidence",
    "supporting_evidence.existing_in_vivo_evidence": "Existing in vivo evidence",
    "supporting_evidence.human_evidence": "Human / clinical evidence",
}

ROLE_EN = {
    0: ("R0", "Unable to assess", "Required information or valid evidence is insufficient to assign a usable evidence role."),
    1: ("R1", "Hypothesis generating", "The evidence may suggest a potential toxicity hazard or mechanism, but it cannot support a safety conclusion or animal-study reduction."),
    2: ("R2", "Early screening", "The evidence can support candidate prioritization and selection of follow-up studies, but it does not support animal-study reduction or replacement."),
    3: ("R3", "Supportive evidence", "The evidence can support an early toxicity assessment when used with other reliable, independent evidence."),
    4: ("R4", "Animal-study reduction support", "Under defined conditions, the evidence may support reducing specific animal numbers, dose groups, sampling, or endpoint scope."),
    5: ("R5", "Candidate replacement for a specific study", "Within a narrowly defined Context of Use, the method may be discussed with experts and regulators as a candidate replacement for a specific endpoint or study component."),
}

ANIMAL_EN = {
    0: ("Unable to assess", "Required information or a valid execution is insufficient."),
    1: ("Insufficient for reduction or replacement", "Do not reduce the existing toxicity-assessment plan until additional evidence is obtained."),
    2: ("Use for screening only", "The evidence may guide candidate prioritization and follow-up testing, but it does not support animal-study reduction."),
    3: ("Supportive for study refinement", "The evidence may help refine the animal-study design, but additional validation is required before reducing the study."),
    4: ("Supports limited reduction", "Within the stated conditions and endpoint, reduction of animal numbers, dose groups, or duplicate studies may be considered."),
    5: ("Candidate replacement for a specific study", "Within a narrowly defined Context of Use, the method may be considered for expert and regulatory discussion as a replacement candidate."),
}

GAP_EN: dict[str, tuple[str, str, str, str, str]] = {
    "ET-G000": ("Outside active MVP scope", "The detailed rules in this version are limited to early hepatotoxicity.", "Decision-limiting", "Evidence Role R0", "Assess within the early-hepatotoxicity vertical slice or add a validated endpoint module."),
    "ET-G000B": ("No assessment method", "At least one AI or NAM evidence stream must be provided.", "Decision-limiting", "Evidence Role R0", "Provide at least one AI prediction or NAM result."),
    "ET-G001": ("Toxicity question not defined", "The Question of Interest has not been clearly defined.", "Decision-limiting", "Evidence Role R0", "Define the toxicity question and Context of Use in one clear statement."),
    "ET-G001B": ("Candidate not defined", "The candidate being assessed cannot be identified.", "Decision-limiting", "Evidence Role R0", "Define the candidate name and modality."),
    "ET-G002": ("Insufficient AI model identity", "Both the model name and exact version are required.", "Decision-limiting", "AI result reproducibility and change history cannot be established", "Obtain the model name, version, developer, and model card."),
    "ET-G003": ("AI endpoint mismatch", "The endpoint predicted by the AI model does not match the current toxicity question.", "Decision-limiting", "Not fit for purpose; Evidence Role R0", "Reassess using a method validated for the same endpoint as the toxicity question."),
    "ET-G004": ("Insufficient external AI validation", "Independent external validation or representativeness of the validation population has not been adequately demonstrated.", "Major gap", "Method credibility is limited", "Confirm independent external validation, validation-population characteristics, and confidence intervals."),
    "ET-G005": ("False-negative performance unknown", "False-negative characteristics are required before using a negative prediction in a high-impact decision.", "Decision-limiting", "May cap the negative prediction at Evidence Role R2", "Obtain sensitivity, false-negative rate, and confidence intervals for the relevant endpoint and threshold."),
    "ET-G006": ("AI prediction is out of domain", "The candidate modality or characteristics are not represented in the model's training and validation domain.", "Decision-limiting", "A negative prediction is not accepted as a Reliable Negative; maximum R1", "Use a model that includes the current modality or add an independent orthogonal NAM."),
    "ET-G007": ("AI applicability domain unclear", "It cannot be determined with sufficient confidence whether the candidate lies within the model's applicability domain.", "Major gap", "Use of the AI result is restricted", "Obtain structural similarity, modality coverage, exposure-range, and nearest-neighbor evidence."),
    "ET-G010": ("NAM protocol insufficient", "The method, acceptance criteria, and execution conditions are not described adequately.", "Decision-limiting", "Validity of this NAM execution is restricted", "Complete the protocol, acceptance criteria, statistical decision rule, and deviation record."),
    "ET-G011": ("Positive-control validity insufficient", "A failed or missing positive control prevents this NAM execution from being considered valid.", "Decision-limiting", "Classify the NAM result as uninterpretable", "Repeat or confirm the assay with a valid positive control."),
    "ET-G012": ("Negative-control validity insufficient", "A failed or missing negative control prevents adequate interpretation of background response.", "Decision-limiting", "Classify the NAM result as uninterpretable", "Add a valid negative control and background-response acceptance criteria."),
    "ET-G013": ("NAM reproducibility evidence insufficient", "Reproducibility across donors, lots, or repeat experiments has not been established.", "Major gap", "Method credibility is limited", "Assess reproducibility across donors, lots, experimental days, and, where feasible, external laboratories."),
    "ET-G014": ("Insufficient human-relevant NAM evidence", "An AI prediction alone cannot adequately establish human biological relevance.", "Major gap", "Human relevance and Evidence Role are limited", "Add a human-derived liver model, clinical-class evidence, or mechanistic evidence based on human tissue."),
    "ET-G015": ("Hepatocyte component missing", "A hepatotoxicity Context of Use requires relevant hepatocyte function.", "Decision-limiting", "Low human relevance", "Include functionally characterized human hepatocytes."),
    "ET-G016": ("Immune/Kupffer-cell response not assessed", "For nanoparticles or oligonucleotides, uncertainty in hepatic immune response remains substantial.", "Major gap", "Human relevance and immune-mechanism interpretation are limited", "Add Kupffer-cell coculture, cytokine assessment, or another immune-competent liver model."),
    "ET-G017": ("Metabolic competence not characterized", "Human hepatotoxicity translation is limited because CYP and hepatic metabolic functions have not been characterized.", "Major gap", "Metabolite-mediated toxicity assessment is limited", "Use a test system with characterized CYP and core hepatic functions."),
    "ET-G018": ("Expected human exposure unavailable", "Without Cmax or AUC, test exposure cannot be compared directly with expected human exposure.", "Major gap", "Exposure relevance is limited", "Define expected human Cmax/AUC or an initial PK assumption."),
    "ET-G019": ("Free/intracellular exposure not measured", "Nominal concentration alone does not demonstrate actual cellular or target-tissue exposure.", "Decision-limiting", "A negative NAM result is not accepted as a Reliable Negative", "Measure free or intracellular exposure separately from nominal concentration."),
    "ET-G020": ("No QIVIVE/PBPK linkage", "The NAM result has not been quantitatively translated to planned human exposure.", "Major gap", "Human-exposure translation is limited", "Use QIVIVE or PBPK to connect NAM concentrations with human exposure."),
    "ET-G021": ("Single/repeated exposure mismatch", "Planned repeated or continuous exposure is supported only by an acute single-exposure assay.", "Decision-limiting", "May cap exposure relevance and Evidence Role at R2", "Obtain a repeated-exposure NAM or a scientifically justified acute-to-repeat bridge."),
    "ET-G022": ("Tissue-distribution evidence insufficient", "Target-organ exposure and accumulation potential cannot be established.", "Major gap", "Target-tissue exposure translation is limited", "Obtain quantitative liver/spleen biodistribution and time-course persistence data."),
    "ET-G023": ("Conflicting evidence", "AI and human-relevant NAM results point in opposite directions. Animal-study reduction cannot be supported until the conflict is resolved.", "Decision-limiting", "Maximum Evidence Role R2; expert review required", "Perform an orthogonal assay and an independent expert review to resolve the conflict."),
    "ET-G024": ("Insufficient independent evidence streams", "A single result cannot constitute a weight-of-evidence assessment.", "Major gap", "R4/R5 cannot be assigned", "Add a second independent evidence stream."),
    "ET-G025": ("Carrier-only control missing", "The toxic contribution of the carrier cannot be separated from that of the formulated product.", "Decision-limiting", "Formulation contribution cannot be assessed", "Use carrier-only and active-only controls to separate toxicity contributions."),
    "ET-G026": ("Evidence traceability insufficient", "The conclusion cannot be traced to documents, pages, tables, or raw data.", "Decision-limiting", "Maximum Evidence Role R2", "Connect every Assertion to a document, page/table, and source data location."),
    "ET-G027": ("Version record insufficient", "Model, assay, ontology, or rule-set versions have not been locked.", "Major gap", "Reproducibility and reassessment scope are unclear", "Record the model, NAM, ontology, and rule-set versions."),
    "ET-G028": ("Structured evidence not reviewed", "Evidence Assertions extracted by AI have not yet been reviewed by an expert.", "Major gap", "High-impact conclusion is held", "Require a toxicology expert to approve, correct, or reject the extracted Assertions."),
}

GAP_EN.update({
    "AI-G001": ("Training-data source/version incomplete", "The source and exact version of the training and validation data are not both available.", "Major gap", "Data lineage and reproducibility are limited", "Record the data source, version, generation date, and immutable hash."),
    "AI-G002": ("Training sample size unknown", "The number of samples used for model development is not available.", "Major gap", "Precision and representativeness of the performance estimates are limited", "Report the total sample size and endpoint-specific positive/negative distribution."),
    "AI-G003": ("Class balance unknown", "The prevalence of toxicity-positive labels and class imbalance have not been reported.", "Major gap", "Accuracy and AUROC are difficult to interpret", "Report prevalence, class balance, and imbalance-handling methods."),
    "AI-G004": ("Data-split strategy unclear", "It is unclear whether random, scaffold, temporal, or external splitting was used.", "Major gap", "Generalization performance is difficult to interpret", "Document the split unit, timing, and independence of training, tuning, and test sets."),
    "AI-G005": ("Test set is non-independent or overlapping", "Training and test/external-validation data are not independent, or duplicate/near-duplicate items were identified.", "Decision-limiting", "Reported validation performance cannot be accepted as independent predictivity", "Remove overlap and repeat validation on an independent scaffold, temporal, or external test set."),
    "AI-G006": ("Test-set independence insufficient", "Independence and analog overlap across training, tuning, and test sets have not been adequately demonstrated.", "Major gap", "External-validation credibility is limited", "Assess overlap at compound, salt, stereoisomer, scaffold, and source levels."),
    "AI-G007": ("Data leakage confirmed", "Outcome information or evaluation data leaked into the model-development pipeline.", "Decision-limiting", "Performance evaluation is invalid; maximum Evidence Role R1", "Repeat the full pipeline after an independent split, including preprocessing and feature selection."),
    "AI-G008": ("Data-leakage assessment insufficient", "Leakage assessment across preprocessing, feature selection, analog overlap, and target-derived features is incomplete.", "Major gap", "Model performance may be overestimated", "Perform and document an end-to-end leakage assessment using an independent pipeline."),
    "AI-G009": ("Duplicate/analog assessment insufficient", "Exact duplicates, salts, stereoisomers, or near scaffolds across data splits have not been excluded.", "Major gap", "Validation independence is limited", "Normalize structures and assess exact and scaffold-level overlap."),
    "AI-G010": ("Endpoint definition missing", "The clinical, pathology, or assay meaning of the positive and negative labels is not defined.", "Decision-limiting", "The model output cannot be aligned with the Question of Interest", "Define the endpoint, time window, severity threshold, and positive/negative criteria."),
    "AI-G011": ("Ground truth unclear", "The reference standard used to generate model labels cannot be identified.", "Decision-limiting", "Model performance and clinical meaning are limited", "Link the labels to expert adjudication, pathology, a validated assay, or another explicit reference method."),
    "AI-G012": ("Label quality limited", "The toxicity labels lack evidence of expert consensus or independent review.", "Major gap", "Ground-truth error may propagate into model performance", "Use blinded expert review, adjudication, or label-uncertainty analysis."),
    "AI-G013": ("Untested data labeled negative", "Not-tested or not-reported records were assigned to the negative toxicity class.", "Decision-limiting", "Negative-class contamination and false reassurance risk", "Separate untested, missing, and unreported states from true negative labels."),
    "AI-G014": ("Missing-label policy insufficient", "The separation of untested, missing, unreported, and truly negative records is unclear.", "Major gap", "Negative-label reliability is limited", "Document the missingness taxonomy and label-assignment rule."),
    "AI-G015": ("Toxicity time window undefined", "The model does not clearly distinguish acute, repeated, delayed, or cumulative toxicity.", "Major gap", "Alignment with the intended dosing duration is limited", "Define the observation window and align it with the current Context of Use."),
    "AI-G016": ("Severity threshold undefined", "The model does not distinguish minor changes from adverse or clinically important toxicity.", "Major gap", "Development meaning of a positive result is unclear", "Define severity/adversity thresholds and the adjudication process."),
    "AI-G017": ("Core classification metrics missing", "Sensitivity or specificity is not reported.", "Decision-limiting", "Accuracy alone is insufficient for toxicity-model evaluation", "Report sensitivity, specificity, and a threshold-specific confusion matrix."),
    "AI-G018": ("Negative-prediction performance incomplete", "False-negative rate or NPV is missing for the current negative prediction.", "Decision-limiting", "Prediction Reliability is capped at moderate", "Report FNR and NPV at the relevant endpoint, prevalence, and threshold."),
    "AI-G019": ("PPV missing for positive prediction", "The proportion of positive predictions that are true positives is unavailable.", "Major gap", "Prioritization of confirmatory testing is limited", "Report PPV and its confidence interval at the current prevalence and threshold."),
    "AI-G020": ("Performance confidence intervals incomplete", "Confidence intervals are available for only some core performance metrics.", "Major gap", "Precision of performance estimates is limited", "Report 95% confidence intervals for core metrics and relevant subgroups."),
    "AI-G021": ("Performance confidence intervals missing", "Point estimates alone do not characterize statistical uncertainty in model performance.", "Major gap", "Performance-estimate precision is unknown", "Report confidence intervals for sensitivity, specificity, PPV/NPV, AUROC, and AUPRC."),
    "AI-G022": ("Decision threshold missing", "The threshold used to classify positive and negative predictions is unavailable.", "Decision-limiting", "The prediction class cannot be reproduced", "Report the threshold, its intended purpose, and the false-positive/false-negative trade-off."),
    "AI-G023": ("External-validation representativeness insufficient", "The external-validation population may not represent the current modality, endpoint, exposure range, or intended population.", "Major gap", "Generalization to the current COU is limited", "Compare the external-validation population with the candidate and current Context of Use."),
    "AI-G024": ("AUPRC missing for a rare positive class", "When toxicity-positive cases are rare, AUROC or accuracy alone may be misleading.", "Major gap", "Rare-toxicity detection performance is unknown", "Report the precision-recall curve and AUPRC with confidence intervals."),
    "AI-G025": ("Sensitivity and FNR are inconsistent", "For the same dataset and threshold, FNR should generally equal 100%-sensitivity, but the reported values differ materially.", "Decision-limiting", "Metric denominators, thresholds, or datasets may have been mixed", "Reconcile the dataset, threshold, denominator, and confidence interval for each metric."),
    "AI-G026": ("Meaning of output percentage unclear", "The displayed percentage is not confirmed as a calibrated probability rather than a raw score or ensemble agreement.", "Decision-limiting", "The value cannot be presented as an actual toxicity probability", "Define the output and avoid probability/confidence language for uncalibrated scores."),
    "AI-G027": ("Calibration insufficient", "Agreement between model output and observed event rates has not been validated.", "Major gap", "The output cannot be interpreted as an actual risk probability", "Provide a reliability curve, Brier score, and calibration slope/intercept."),
    "AI-G028": ("Reproducibility metadata incomplete", "Code commit, software environment, or training-data hash is missing.", "Major gap", "Prediction reproduction and change-impact tracking are limited", "Record the code commit, locked software environment, and dataset hash."),
    "AI-G029": ("Lifecycle/drift management insufficient", "Procedures for performance degradation, drift, threshold changes, and revalidation are incomplete.", "Major gap", "R4/R5 and repeated operational use are limited", "Define drift triggers, change control, revalidation criteria, and retrospective reassessment procedures."),
    "AI-G030": ("Individual-prediction input quality unverified", "The structure, salt, stereoisomer, sequence, formulation, or input features have not been verified against the candidate.", "Decision-limiting", "Individual Prediction Reliability is capped at moderate", "Verify identity, structure/sequence normalization, and relevant batch/formulation information."),
    "AI-G031": ("OOD detection evidence insufficient", "There is insufficient quantitative evidence that the candidate lies within the training distribution.", "Major gap", "Objectivity of applicability assessment is limited", "Report nearest-neighbor distance, leverage, domain density, or a dedicated OOD detector."),
    "AI-G032": ("Biological explainability limited", "Model features are not adequately connected to a plausible toxicity mechanism, product characteristic, or measurable endpoint.", "Major gap", "Mechanistic interpretation and follow-up-study design are limited", "Connect prediction explanations with known toxicity mechanisms and orthogonal NAM endpoints."),
})

GATE_EN: dict[str, tuple[str, str]] = {
    "독성 질문·COU": ("Toxicity question & COU", "The question and candidate must be defined."),
    "방법 식별·버전": ("Method identity & version", "An exact model or method version is required."),
    "Endpoint 일치": ("Endpoint match", "The method endpoint must match the toxicity question."),
    "후보 적용범위": ("Candidate applicability", "The candidate must be inside or near the method's applicability domain."),
    "NAM 실행 유효성": ("NAM execution validity", "Controls and execution status must be valid."),
    "사람 관련성": ("Human relevance", "Relevant cells, metabolic function, and immune competence must be assessed."),
    "노출 번역": ("Exposure translation", "Actual exposure and linkage to human exposure are required."),
    "독립 근거": ("Independent evidence", "At least two independent evidence streams are required for R4/R5."),
    "근거 추적성": ("Evidence traceability", "Evidence must be traceable to documents, pages, tables, and source data."),
    "전문가 검토": ("Expert review", "Toxicology expert approval is mandatory for R4/R5."),
}

SCORE_EN = {
    "방법 신뢰성": "Method credibility",
    "후보 적용성": "Candidate applicability",
    "사람 생물학적 관련성": "Human biological relevance",
    "노출 관련성": "Exposure relevance",
    "근거 일치성": "Evidence concordance",
    "잔여 불확실성": "Residual uncertainty",
}

GATE_EN.update({
    "Endpoint·Ground Truth": ("Endpoint & ground truth", "Review the endpoint definition, reference standard, label quality, and missing-label policy."),
    "데이터 독립성·Leakage": ("Data independence & leakage", "Review independence across data splits and end-to-end leakage controls."),
    "예측성능·불확실성": ("Predictive performance & uncertainty", "Review sensitivity, specificity, predictive values, threshold, AUPRC, and confidence intervals."),
    "확률 Calibration": ("Probability calibration", "Confirm whether the displayed percentage is a calibrated probability."),
    "개별 예측 신뢰성": ("Individual Prediction Reliability", "Review input quality, domain fit, OOD evidence, and prediction uncertainty for the candidate."),
    "AI Lifecycle·Governance": ("AI lifecycle & governance", "Review versioning, code/data lineage, drift monitoring, and change control."),
})

SCORE_EN.update({
    "데이터 신뢰성": "Data credibility",
    "Endpoint·Ground Truth 적절성": "Endpoint & ground-truth adequacy",
    "예측성능 적절성": "Predictive-performance adequacy",
    "Calibration 적절성": "Calibration adequacy",
    "개별 예측 신뢰성": "Individual Prediction Reliability",
    "Lifecycle·Governance": "Lifecycle & governance",
})

TOXICITY_DIRECTION_EN = {
    "일관된 양성 신호": "Concordant positive signal",
    "양성 신호": "Positive signal",
    "상충": "Conflicting evidence",
    "일관된 음성 신호": "Concordant negative signal",
    "음성 신호": "Negative signal",
    "불확실": "Uncertain",
    "평가 불가": "Unable to assess",
}

DEVELOPMENT_CONCERN_EN = {
    "높음 — 신뢰 가능한 독성신호의 확인·기전규명 우선": "High — prioritize confirmation and mechanistic characterization of a credible toxicity signal",
    "중간–높음 — 양성신호 확인 필요": "Moderate to high — positive signal requires confirmation",
    "중간–높음 — 상충 근거 해소 전 낮게 분류 불가": "Moderate to high — cannot be considered low until conflicting evidence is resolved",
    "미정 — 경계 또는 불확실한 결과": "Unknown — borderline or uncertain result",
    "낮음 — 정의된 Context of Use 내": "Low — within the defined Context of Use",
    "낮음–중간 — 추가 확인과 사용범위 제한 필요": "Low to moderate — additional confirmation and use restrictions are required",
    "미정 — 음성결과만으로 낮게 분류할 수 없음": "Unknown — a negative result alone cannot support a low-concern conclusion",
    "평가 불가": "Unable to assess",
}

ANIMAL_STATUS_EN = {
    "평가 불가": "Unable to assess",
    "축소·대체 근거 불충분": "Insufficient for reduction or replacement",
    "선별 용도로만 사용": "Use for screening only",
    "보조·정교화 가능": "Supportive for study refinement",
    "제한적 축소 지원": "Supports limited reduction",
    "특정 시험 대체 후보": "Candidate replacement for a specific study",
    "축소보다 독성신호 확인 우선": "Prioritize toxicity-signal confirmation over reduction",
    "동물시험 축소 미지원": "Animal-study reduction not supported",
    "축소 판단 보류": "Hold reduction decision",
}

ANIMAL_DESCRIPTION_EN = {
    "현재 근거는 독성신호의 확인, 기전규명, 노출-반응 및 표적화된 후속시험을 우선하도록 지지합니다. 단순 동물시험 축소로 해석해서는 안 됩니다.": "The current evidence supports prioritizing toxicity-signal confirmation, mechanistic characterization, exposure-response analysis, and targeted follow-up testing. It must not be interpreted as a simple basis for animal-study reduction.",
    "상충 원인을 독립적으로 확인하기 전에는 동물시험 축소 또는 대체를 지지하지 않습니다.": "Animal-study reduction or replacement is not supported until the cause of the conflicting evidence is independently resolved.",
    "Evidence Role이 높더라도 Development Concern이 미정이면 동물시험 축소 결론을 보류합니다.": "Even when the Evidence Role is high, an animal-study reduction conclusion is held when Development Concern remains unknown.",
}

REVIEW_STATUS_EN = {"제안됨": "Proposed", "승인": "Approved", "수정": "Corrected", "거절": "Rejected"}
REVIEW_STATUS_KO = {value: key for key, value in REVIEW_STATUS_EN.items()}
VALUE_KO = {value: key for key, value in VALUE_EN.items()}

ASSERTION_COLUMNS = {
    "ko": {
        "Assertion ID": "Assertion ID", "분류": "분류", "평가 필드": "평가 필드", "Field Path": "Field Path",
        "제안/수정 값": "제안/수정 값", "형식": "형식", "출처 문서": "출처 문서", "출처 위치": "출처 위치",
        "근거 발췌": "근거 발췌", "추출 신뢰도": "추출 신뢰도", "검토 상태": "검토 상태", "검토 메모": "검토 메모",
    },
    "en": {
        "Assertion ID": "Assertion ID", "분류": "Category", "평가 필드": "Assessment Field", "Field Path": "Field Path",
        "제안/수정 값": "Proposed / Corrected Value", "형식": "Value Type", "출처 문서": "Source Document", "출처 위치": "Source Location",
        "근거 발췌": "Evidence Excerpt", "추출 신뢰도": "Extraction Confidence", "검토 상태": "Review Status", "검토 메모": "Reviewer Note",
    },
}

DOCUMENT_COLUMNS = {
    "ko": {"문서 ID": "문서 ID", "파일명": "파일명", "형식": "형식", "크기(KB)": "크기(KB)", "근거 구간": "근거 구간", "추출 문자": "추출 문자", "경고": "경고", "SHA-256": "SHA-256"},
    "en": {"문서 ID": "Document ID", "파일명": "File Name", "형식": "Format", "크기(KB)": "Size (KB)", "근거 구간": "Evidence Segments", "추출 문자": "Characters Extracted", "경고": "Warnings", "SHA-256": "SHA-256"},
}


def text(key: str, lang: str = "ko", **kwargs: Any) -> str:
    record = UI_TEXT.get(key)
    value = record.get(lang, record.get("ko", key)) if record else key
    return value.format(**kwargs) if kwargs else value


def page_label(page_id: str, lang: str = "ko") -> str:
    return text(PAGE_KEYS.get(page_id, page_id), lang)


def value_label(value: Any, lang: str = "ko") -> str:
    if value is None:
        return ""
    raw = str(value)
    if lang == "ko":
        return raw
    return VALUE_EN.get(raw, CASE_EN.get(raw, CATEGORY_EN.get(raw, raw)))


def case_label(value: str, lang: str = "ko") -> str:
    return value if lang == "ko" else CASE_EN.get(value, value)


def category_label(value: str, lang: str = "ko") -> str:
    return value if lang == "ko" else CATEGORY_EN.get(value, value)


def assertion_field_label(assertion: EvidenceAssertion, lang: str = "ko") -> str:
    if lang == "ko":
        return assertion.label_ko
    return FIELD_PATH_EN.get(assertion.field_path, assertion.label_ko)


def review_status_label(value: str, lang: str = "ko") -> str:
    return value if lang == "ko" else REVIEW_STATUS_EN.get(value, value)


def review_status_internal(value: str, lang: str = "ko") -> str:
    if lang == "ko":
        return value
    return REVIEW_STATUS_KO.get(value, value)


def value_internal(value: Any, lang: str = "ko") -> str:
    raw = str(value)
    if lang == "ko":
        return raw
    return VALUE_KO.get(raw, raw)


def role_definition(role: int, lang: str = "ko") -> tuple[str, str, str]:
    if lang == "en":
        return ROLE_EN[role]
    from .engine import ROLE_DEFINITIONS
    return ROLE_DEFINITIONS[role]


def animal_use_definition(role: int, lang: str = "ko") -> tuple[str, str]:
    if lang == "en":
        return ANIMAL_EN[role]
    return {
        0: ("평가 불가", "필수정보 또는 유효한 실행이 부족합니다."),
        1: ("축소·대체 근거 불충분", "추가 근거 확보 전 기존 독성평가를 축소해서는 안 됩니다."),
        2: ("선별 용도로만 사용", "후보 우선순위와 추가시험 선택에는 사용할 수 있으나 동물시험 축소는 지지하지 않습니다."),
        3: ("보조·정교화 가능", "동물시험 설계 정교화에는 활용할 수 있으나 축소에는 추가 검증이 필요합니다."),
        4: ("제한적 축소 지원", "명시된 조건과 endpoint에서 동물 수·용량군·중복시험 축소를 검토할 수 있습니다."),
        5: ("특정 시험 대체 후보", "좁게 정의된 Context of Use에서 전문가 및 규제기관 논의를 위한 대체 후보입니다."),
    }[role]


def localize_gap(gap: DataGap, lang: str = "ko") -> dict[str, str]:
    if lang == "ko":
        return gap.to_dict()
    title, description, criticality, effect, recommendation = GAP_EN.get(
        gap.code,
        (gap.title, gap.description, value_label(gap.criticality, lang), gap.effect, gap.recommendation),
    )
    return {
        "code": gap.code,
        "title": title,
        "description": description,
        "criticality": criticality,
        "rule_id": gap.rule_id,
        "effect": effect,
        "recommendation": recommendation,
    }


def _gate_effect_en(gate: GateResult) -> str:
    mapping = {
        "미통과 시 R0": "R0 if failed",
        "미통과 시 R0 또는 R1": "R0 or R1 if failed",
        "Out-of-domain 음성은 최대 R1": "An out-of-domain negative is capped at R1",
        "무효 실행은 근거 제외": "Invalid execution is excluded from the evidence package",
        "낮으면 R3 이상 제한": "Low performance limits R3 or higher",
        "R4/R5에 최소 2개 필요": "At least two streams are required for R4/R5",
        "미통과 시 최대 R2": "Maximum R2 if failed",
        "미검토 시 최대 R3": "Maximum R3 if not reviewed",
    }
    return mapping.get(gate.effect, gate.effect)


def localize_gate(gate: GateResult, lang: str = "ko") -> dict[str, str]:
    if lang == "ko":
        return gate.to_dict()
    name, default_rationale = GATE_EN.get(gate.gate, (gate.gate, gate.rationale))
    rationale = default_rationale
    if gate.gate == "후보 적용범위" and gate.rationale.startswith("AI domain status:"):
        rationale = gate.rationale
    elif gate.gate == "독립 근거":
        digits = "".join(ch for ch in gate.rationale if ch.isdigit())
        rationale = f"{digits or '0'} independent evidence stream(s)"
    return {
        "gate": name,
        "status": value_label(gate.status, lang),
        "rationale": rationale,
        "effect": _gate_effect_en(gate),
    }


def _english_observations(inp: AssessmentInput) -> list[str]:
    product = inp.product
    ai = inp.ai_model
    nam = inp.nam_assay
    items = [
        f"The assessment target is {product.product_name or 'an unspecified candidate'}; the product modality is {value_label(product.modality, 'en')} and the route is {value_label(product.route, 'en')}.",
    ]
    if ai.use_ai:
        items.append(
            f"AI model {ai.model_name or '(model name unavailable)'} {ai.model_version or '(version unavailable)'} produced a {value_label(ai.result, 'en')} result."
        )
    if nam.use_nam:
        items.append(
            f"The {value_label(nam.nam_type, 'en')} NAM produced a {value_label(nam.result, 'en')} result using a {value_label(nam.exposure_design, 'en')} design."
        )
    return items


def _english_interpretations(inp: AssessmentInput, result: AssessmentResult) -> list[str]:
    ai = inp.ai_model
    nam = inp.nam_assay
    product = inp.product
    domain = result.audit.get("ai_domain_status")
    items: list[str] = []
    if ai.use_ai and domain == "Out-of-domain":
        items.append("Regardless of the model's general performance, the candidate is outside the model's applicability domain; therefore, a negative prediction cannot be interpreted as evidence of low toxicity concern.")
    if nam.use_nam and nam.result == "음성" and nam.measured_exposure == "측정 안 됨":
        items.append("The negative NAM result is not a Reliable Negative because free or intracellular exposure was not demonstrated.")
    if nam.use_nam and product.exposure_pattern in {"반복 노출", "지속 노출"} and nam.exposure_design == "단회/급성 노출":
        items.append("An acute single-exposure NAM is being used to support a repeated or continuous dosing plan, leaving uncertainty about accumulation, adaptation, and delayed toxicity.")
    if ai.use_ai and ai.probability_percent is not None and ai.probability_type != "보정된 확률":
        items.append("The displayed percentage has not been confirmed as a calibrated probability and therefore must not be described as the actual probability of toxicity.")
    if ai.use_ai and ai.leakage_assessment in {"누수 확인", "누수 가능성"}:
        items.append("Possible data leakage may have inflated the reported validation performance.")
    if any(gap.code == "ET-G023" for gap in result.data_gaps):
        items.append("AI and NAM evidence conflict. Neither result should be prioritized until the cause of the discordance is investigated and independently confirmed.")
    if result.toxicity_direction in {"일관된 양성 신호", "양성 신호"}:
        items.append("High evidence credibility does not imply safety; it may instead indicate that the positive toxicity signal itself is more credible.")
    if not items:
        items.append("Considering data credibility, ground truth, predictive performance, candidate applicability, human relevance, and exposure relevance, the evidence may be used only within the defined scope together with other independent evidence.")
    return items


def localize_result(result: AssessmentResult, inp: AssessmentInput, lang: str = "ko") -> dict[str, Any]:
    if lang == "ko":
        return {
            "evidence_role": result.evidence_role,
            "evidence_role_code": result.evidence_role_code,
            "evidence_role_name": result.evidence_role_name,
            "evidence_role_description": result.evidence_role_description,
            "animal_use_status": result.animal_use_status,
            "animal_use_description": result.animal_use_description,
            "model_risk": result.model_risk,
            "residual_uncertainty": result.residual_uncertainty,
            "evidence_stream_count": result.evidence_stream_count,
            "evidence_confidence": result.evidence_confidence,
            "toxicity_direction": result.toxicity_direction,
            "prediction_reliability": result.prediction_reliability,
            "development_concern": result.development_concern,
            "ai_credibility_profile": result.ai_credibility_profile,
            "scores": result.scores,
            "gates": [gate.to_dict() for gate in result.gates],
            "data_gaps": [gap.to_dict() for gap in result.data_gaps],
            "observations": result.observations,
            "interpretations": result.interpretations,
            "development_relevance": result.development_relevance,
            "recommendations": result.recommendations,
            "audit": result.audit,
        }
    role_code, role_name, role_desc = role_definition(result.evidence_role, "en")
    animal_status = ANIMAL_STATUS_EN.get(result.animal_use_status, result.animal_use_status)
    animal_desc = ANIMAL_DESCRIPTION_EN.get(result.animal_use_description, animal_use_definition(result.evidence_role, "en")[1])
    localized_gaps = [localize_gap(gap, "en") for gap in result.data_gaps]
    recommendations = list(dict.fromkeys(gap["recommendation"] for gap in localized_gaps))
    if not recommendations:
        recommendations = ["Document the conditions and limits of the current Evidence Role, and obtain expert and, where appropriate, regulatory review before changing an animal-study plan."]
    evidence_confidence = value_label(result.evidence_confidence, "en")
    toxicity_direction = TOXICITY_DIRECTION_EN.get(result.toxicity_direction, result.toxicity_direction)
    prediction_reliability = value_label(result.prediction_reliability, "en")
    development_concern = DEVELOPMENT_CONCERN_EN.get(result.development_concern, result.development_concern)
    development_relevance = [
        f"The current evidence package is classified as {role_code} — {role_name}.",
        f"Evidence Confidence is {evidence_confidence}; Toxicity Direction is {toxicity_direction}; Development Concern is {development_concern}.",
        animal_desc,
        f"Residual uncertainty is {value_label(result.residual_uncertainty, 'en')}, and model risk is {value_label(result.model_risk, 'en')}.",
    ]
    return {
        "evidence_role": result.evidence_role,
        "evidence_role_code": role_code,
        "evidence_role_name": role_name,
        "evidence_role_description": role_desc,
        "animal_use_status": animal_status,
        "animal_use_description": animal_desc,
        "model_risk": value_label(result.model_risk, "en"),
        "residual_uncertainty": value_label(result.residual_uncertainty, "en"),
        "evidence_stream_count": result.evidence_stream_count,
        "evidence_confidence": evidence_confidence,
        "toxicity_direction": toxicity_direction,
        "prediction_reliability": prediction_reliability,
        "development_concern": development_concern,
        "ai_credibility_profile": {SCORE_EN.get(key, key): value_label(value, "en") if isinstance(value, str) else value for key, value in result.ai_credibility_profile.items()},
        "scores": {SCORE_EN.get(key, key): value_label(value, "en") if isinstance(value, str) else value for key, value in result.scores.items()},
        "gates": [localize_gate(gate, "en") for gate in result.gates],
        "data_gaps": localized_gaps,
        "observations": _english_observations(inp),
        "interpretations": _english_interpretations(inp, result),
        "development_relevance": development_relevance,
        "recommendations": recommendations,
        "audit": {**result.audit, "prototype_boundary": "Early-hepatotoxicity vertical slice; for research and decision support only"},
    }


def localize_document_row(row: dict[str, Any], lang: str = "ko") -> dict[str, Any]:
    labels = DOCUMENT_COLUMNS[lang]
    return {labels.get(key, key): value for key, value in row.items()}


def localize_assertion_row(row: dict[str, Any], assertion: EvidenceAssertion, lang: str = "ko") -> dict[str, Any]:
    labels = ASSERTION_COLUMNS[lang]
    converted: dict[str, Any] = {}
    for key, value in row.items():
        display_key = labels.get(key, key)
        if key == "분류":
            value = category_label(str(value), lang)
        elif key == "평가 필드":
            value = assertion_field_label(assertion, lang)
        elif key == "제안/수정 값":
            value = value_label(value, lang)
        elif key == "검토 상태":
            value = review_status_label(str(value), lang)
        converted[display_key] = value
    return converted


def internalize_assertion_row(row: dict[str, Any], lang: str = "ko") -> dict[str, Any]:
    if lang == "ko":
        return row
    reverse_columns = {value: key for key, value in ASSERTION_COLUMNS["en"].items()}
    converted = {reverse_columns.get(key, key): value for key, value in row.items()}
    converted["검토 상태"] = review_status_internal(str(converted.get("검토 상태", "")), "en")
    converted["제안/수정 값"] = value_internal(converted.get("제안/수정 값", ""), "en")
    return converted


AUDIT_ACTION_EN = {
    "프로젝트 생성": "Project created",
    "프로젝트 메타데이터 수정": "Project metadata updated",
    "로컬 프로젝트 저장": "Project saved locally",
    "로컬 프로젝트 불러오기": "Local project loaded",
    "JSON 프로젝트 불러오기": "JSON project imported",
    "Golden Case 불러오기": "Golden Case loaded",
    "컨설팅 사례 불러오기": "Consulting case loaded",
    "문서 및 Assertion 추가": "Documents and Assertions added",
    "문서 삭제": "Document deleted",
    "Assertion 검토 저장": "Assertion review saved",
    "Assertion 일괄 승인": "Assertions approved in bulk",
    "승인 Assertion 적용": "Reviewed Assertions applied",
    "구조화 평가 입력 저장": "Structured assessment input saved",
    "EarlyTox 평가 실행": "EarlyTox assessment run",
}


def audit_action_label(action: str, language: str = "ko") -> str:
    if language != "en":
        return action
    return AUDIT_ACTION_EN.get(action, action)


def audit_detail_label(detail: str, language: str = "ko") -> str:
    if language != "en":
        return detail
    import re

    text_value = str(detail or "")
    replacements = {
        "후보 미입력": "Candidate not entered",
        "독성책임자": "Toxicology lead",
        "프로그램 독성책임자": "Program toxicology lead",
        "현재 사용자": "Current user",
        "가설 생성": "Hypothesis generating",
        "초기 선별": "Screening use",
        "보조 근거": "Supportive evidence",
        "동물시험 축소 지원": "Reduction-supporting evidence",
        "특정 시험 대체 후보": "Candidate replacement for a specific study",
    }
    for source, target in replacements.items():
        text_value = text_value.replace(source, target)
    text_value = re.sub(r"문서\s*(\d+)개,\s*Assertion\s*(\d+)개", r"\1 document(s), \2 Assertion(s)", text_value)
    text_value = re.sub(r"필터 결과\s*(\d+)개", r"\1 filtered item(s)", text_value)
    text_value = re.sub(r"승인·수정\s*(\d+)개", r"\1 approved/corrected item(s)", text_value)
    text_value = re.sub(r"^(\d+)개$", r"\1 item(s)", text_value)
    return text_value
