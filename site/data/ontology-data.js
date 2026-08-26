window.NORA_ONTOLOGY = {
  "meta": {
    "name": "ToxiGuard Preclinical Toxicology Ontology — EarlyTox Extension",
    "shortName": "TG-PTO-ET",
    "version": "1.0-site",
    "product": "ToxiGuard NORA EarlyTox",
    "purpose": "AI 및 NAM 기반 초기 독성근거가 특정 후보물질과 정의된 개발 의사결정에서 어디까지 신뢰 가능하고 사용할 수 있는지를 구조화"
  },
  "principles": [
    "높은 모델 정확도는 현재 후보물질에 대한 높은 적용성을 의미하지 않는다.",
    "음성 AI 예측은 독성 부재를 의미하지 않는다.",
    "음성 NAM 결과는 자동으로 신뢰 가능한 음성이 아니다.",
    "적용범위 밖 예측은 신뢰 가능한 근거가 아니다.",
    "명목농도는 표적세포 또는 표적조직 노출과 동일하지 않다.",
    "하나의 근거 흐름은 Weight of Evidence가 아니다.",
    "특정 endpoint 대체는 전체 독성패키지 대체가 아니다.",
    "자료 없음은 음성 근거가 아니다.",
    "불확실성은 낮은 독성우려로 계산하지 않는다."
  ],
  "chain": [
    {
      "id": "decision",
      "label": "개발 의사결정",
      "en": "Development Decision",
      "description": "NORA가 지원하려는 구체적인 개발 판단"
    },
    {
      "id": "product",
      "label": "제품·노출 맥락",
      "en": "Product & Exposure Context",
      "description": "제품 modality, 성분, 전달체, 경로, 용량, 기간과 예정 사람노출"
    },
    {
      "id": "hazard",
      "label": "잠재 독성위험",
      "en": "Potential Toxicity Hazard",
      "description": "제품 특성상 반드시 답해야 하는 이론적 위험"
    },
    {
      "id": "question",
      "label": "핵심 독성질문",
      "en": "Question of Interest",
      "description": "현재 의사결정에서 실제로 답하려는 독성질문"
    },
    {
      "id": "cou",
      "label": "사용범위",
      "en": "Context of Use",
      "description": "AI/NAM의 역할, 범위, endpoint, 개발단계와 제외범위"
    },
    {
      "id": "method",
      "label": "AI·NAM 방법",
      "en": "Alternative Method",
      "description": "특정 버전의 AI 모델, QSAR 또는 사람 관련 NAM"
    },
    {
      "id": "execution",
      "label": "방법 실행",
      "en": "Method Execution",
      "description": "특정 후보와 배치에 대해 수행된 실제 실행과 대조군 유효성"
    },
    {
      "id": "evidence",
      "label": "예측·관찰·근거",
      "en": "Result & Evidence",
      "description": "Prediction, Observation, Finding, Evidence Assertion과 provenance"
    },
    {
      "id": "assessment",
      "label": "신뢰성·적용성 평가",
      "en": "Evidence Assurance",
      "description": "방법, 후보, 사람 생물학, 노출과 근거 일치성 평가"
    },
    {
      "id": "uncertainty",
      "label": "Data Gap·불확실성",
      "en": "Residual Uncertainty",
      "description": "미확인, 상충, 적용범위 이탈과 결정 제한 요소"
    },
    {
      "id": "role",
      "label": "근거 역할",
      "en": "Evidence Role R0–R5",
      "description": "현재 근거를 어디까지 사용할 수 있는지 분류"
    },
    {
      "id": "recommendation",
      "label": "다음 근거·전문가 판단",
      "en": "Next Evidence & Expert Decision",
      "description": "3Rs 권고, 추가시험, 전문가 검토와 감사 추적"
    }
  ],
  "modules": [
    {
      "id": "decision",
      "title": "의사결정 및 Context of Use",
      "subtitle": "Decision & COU Ontology",
      "summary": "AI/NAM을 평가하기 전에 질문, 역할, 범위와 오판 결과를 명시합니다.",
      "classes": [
        {
          "name": "DevelopmentDecision",
          "definition": "NORA를 통해 지원하려는 구체적인 개발 의사결정",
          "children": [
            "EarlyHazardIdentificationDecision",
            "CandidatePrioritizationDecision",
            "AIPredictionValidationDecision",
            "NAMHumanRelevanceDecision",
            "AlternativeEvidenceIntegrationDecision",
            "AnimalReductionDecision",
            "AnimalReplacementCandidateDecision",
            "FollowUpStudyPrioritizationDecision",
            "RegulatoryInteractionPlanningDecision"
          ]
        },
        {
          "name": "QuestionOfInterest",
          "definition": "의사결정에서 답하려는 과학적 질문",
          "children": [
            "HazardIdentificationQuestion",
            "DoseResponseQuestion",
            "ExposureResponseQuestion",
            "MechanisticQuestion",
            "HumanRelevanceQuestion",
            "EvidenceConflictQuestion",
            "AnimalReductionQuestion",
            "AnimalReplacementQuestion"
          ]
        },
        {
          "name": "ContextOfUse",
          "definition": "AI/NAM의 구체적인 역할·범위·사용목적",
          "children": [
            "TargetEndpointScope",
            "ProductScope",
            "ExposureRangeScope",
            "DevelopmentStageScope",
            "PopulationScope",
            "ExcludedUse"
          ]
        },
        {
          "name": "ModelRiskAssessment",
          "definition": "Model Influence와 Decision Consequence에 기반한 위험 평가",
          "children": [
            "ModelInfluenceAssessment",
            "DecisionConsequenceAssessment",
            "ErrorDetectabilityAssessment",
            "MitigationStrengthAssessment"
          ]
        }
      ],
      "properties": [
        "asksQuestion",
        "definesContextOfUse",
        "hasDecisionObjective",
        "hasTargetToxicityEndpoint",
        "hasIntendedEvidenceRole",
        "hasMethodRole",
        "hasMethodScope",
        "hasModelInfluence",
        "hasDecisionConsequence",
        "hasExcludedUse",
        "hasPerformanceRequirement"
      ],
      "validation": [
        "Question of Interest 정확히 1개",
        "Target endpoint 최소 1개",
        "Intended Evidence Role 정확히 1개",
        "Model Influence 및 Decision Consequence 필수",
        "제품과 개발단계 필수"
      ],
      "rules": [
        "높은 Model Influence × 높은 Decision Consequence → 최고 수준의 credibility requirement",
        "COU 미정의 → Evidence Role R0",
        "Endpoint 불일치 → Fit-for-purpose 부적절"
      ]
    },
    {
      "id": "product",
      "title": "제품 및 품질특성",
      "subtitle": "Product & CQA Ontology",
      "summary": "제품 modality와 독성 관련 품질특성을 잠재위험에 연결합니다.",
      "classes": [
        {
          "name": "InvestigationalProduct",
          "definition": "평가 대상 후보물질 또는 시험약",
          "children": [
            "ChemicalDrug",
            "OligonucleotideTherapeutic",
            "siRNAProduct",
            "AntisenseOligonucleotide",
            "mRNAProduct",
            "BiologicalProduct",
            "GeneTherapyProduct",
            "CellTherapyProduct",
            "Nanomedicine",
            "LipidNanoparticle",
            "PolymericNanoparticle",
            "HybridNanoparticle",
            "CombinationProduct"
          ]
        },
        {
          "name": "ProductComponent",
          "definition": "제품을 구성하는 활성·비활성·불순물 요소",
          "children": [
            "ActiveSubstance",
            "TargetingSequence",
            "Carrier",
            "LipidCarrier",
            "PolymericCarrier",
            "ViralVector",
            "InorganicCarrier",
            "Excipient",
            "Conjugate",
            "ProcessRelatedImpurity",
            "ProductRelatedImpurity",
            "DegradationProduct",
            "ResidualSolvent",
            "AdventitiousAgent"
          ]
        },
        {
          "name": "CriticalQualityAttribute",
          "definition": "독성 해석과 시험물질 대표성에 영향을 주는 품질특성",
          "children": [
            "Identity",
            "Purity",
            "Potency",
            "MolecularWeight",
            "ParticleSize",
            "ParticleSizeDistribution",
            "ZetaPotential",
            "Morphology",
            "EncapsulationEfficiency",
            "FreeActiveSubstance",
            "Aggregation",
            "DegreeOfDeacetylation",
            "NucleicAcidIntegrity",
            "SequenceIdentity",
            "SequencePurity",
            "Endotoxin",
            "Sterility",
            "pH",
            "Osmolality",
            "Stability",
            "ReleaseProfile",
            "SurfaceComposition"
          ]
        },
        {
          "name": "ComparabilityAssessment",
          "definition": "독성시험물질과 임상제품의 독성 관련 비교가능성 평가",
          "children": [
            "CompositionComparability",
            "ManufacturingComparability",
            "CQAComparability",
            "ExposureComparability"
          ]
        }
      ],
      "properties": [
        "hasActiveSubstance",
        "hasTargetingSequence",
        "hasCarrier",
        "hasExcipient",
        "hasImpurity",
        "hasManufacturingBatch",
        "hasCriticalQualityAttribute",
        "hasIntendedTarget",
        "hasIntendedMechanism",
        "hasAdministrationRoute",
        "hasExpectedTissueDistribution",
        "createsPotentialHazard",
        "comparesTestArticle",
        "comparesClinicalProduct"
      ],
      "validation": [
        "나노의약품은 particle characterization 필수",
        "전달체 포함 제품은 carrier composition 필수",
        "독성시험물질 배치와 임상제품 대표성 평가 필수",
        "독성 관련 CQA의 출처와 단위 필수"
      ],
      "rules": [
        "Nanomedicine + small-molecule-only model → modality out-of-domain",
        "Carrier 포함 + carrier-only control 누락 → 전달체 기여도 평가 불가",
        "Comparability 불명확 → R4/R5 제한"
      ]
    },
    {
      "id": "toxicity",
      "title": "독성위험 및 기전",
      "subtitle": "Hazard & Mechanism Ontology",
      "summary": "제품특성이 만드는 잠재위험과 이를 해결할 독성질문을 표현합니다.",
      "classes": [
        {
          "name": "PotentialHazard",
          "definition": "제품 특성상 평가가 필요한 이론적 독성위험",
          "children": [
            "OrganToxicityHazard",
            "MechanismBasedHazard",
            "ModalitySpecificHazard",
            "RouteSpecificHazard",
            "FormulationRelatedHazard",
            "ImmuneHazard",
            "GeneticToxicityHazard",
            "ExposureRelatedHazard"
          ]
        },
        {
          "name": "TargetOrgan",
          "definition": "독성소견 또는 잠재위험의 대상 장기",
          "children": [
            "Liver",
            "Kidney",
            "Heart",
            "Lung",
            "Brain",
            "PeripheralNervousSystem",
            "BoneMarrow",
            "Blood",
            "Spleen",
            "Thymus",
            "GastrointestinalTract",
            "EndocrineOrgan",
            "ReproductiveOrgan",
            "InjectionSite",
            "ImmuneSystem"
          ]
        },
        {
          "name": "ToxicityMechanism",
          "definition": "독성발생의 과학적 기전",
          "children": [
            "OnTargetExaggeratedPharmacology",
            "SequenceDependentOffTarget",
            "SequenceIndependentEffect",
            "ReactiveMetaboliteFormation",
            "ImmuneMediatedToxicity",
            "ComplementMediatedToxicity",
            "MitochondrialToxicity",
            "OxidativeStress",
            "MembraneDamage",
            "LysosomalAccumulation",
            "Phospholipidosis",
            "BileAcidTransportInhibition",
            "AccumulationMediatedToxicity",
            "AggregateMediatedToxicity",
            "InfusionRelatedReaction",
            "UnknownMechanism"
          ]
        },
        {
          "name": "HepatotoxicityHazard",
          "definition": "EarlyTox v0.1의 첫 vertical slice",
          "children": [
            "DirectHepatocellularInjury",
            "CholestaticInjury",
            "MixedLiverInjury",
            "MitochondrialDysfunction",
            "ReactiveMetaboliteMediatedInjury",
            "OxidativeStressMediatedInjury",
            "Steatosis",
            "Phospholipidosis",
            "BileAcidTransportDisruption",
            "KupfferCellActivation",
            "ImmuneMediatedLiverInjury",
            "ComplementMediatedHepaticInflammation",
            "LysosomalAccumulation",
            "NanoparticleAccumulation",
            "CarrierMediatedMembraneInjury",
            "SequenceDependentHepaticOffTarget"
          ]
        }
      ],
      "properties": [
        "hasPotentialHazard",
        "raisesToxicityQuestion",
        "hasTargetOrgan",
        "hasMechanism",
        "hasMechanisticPlausibility",
        "isTriggeredByCharacteristic",
        "isModifiedByExposure",
        "isAddressedByMethod"
      ],
      "validation": [
        "PotentialHazard와 Observed Finding 분리",
        "Hazard마다 최소 1개 ToxicityQuestion 연결",
        "사람 관련성 결론에는 기전·노출·표적발현 근거 필요"
      ],
      "rules": [
        "PotentialHazard ≠ ObservedToxicity",
        "Hazard 존재는 독성 양성을 의미하지 않음",
        "미해결 critical hazard → 낮은 concern 분류 불가"
      ]
    },
    {
      "id": "studies",
      "title": "전임상시험 및 시험목적",
      "subtitle": "Nonclinical Study & Purpose Ontology",
      "summary": "시험이 존재하는지가 아니라 어떤 독성질문과 시험목적에 답하는지를 구조화합니다.",
      "classes": [
        {
          "name": "NonclinicalStudy",
          "definition": "개별 약리·PK·독성시험",
          "children": [
            "PharmacologyStudy",
            "PrimaryPharmacodynamicsStudy",
            "SecondaryPharmacodynamicsStudy",
            "SafetyPharmacologyStudy",
            "PharmacokineticStudy",
            "ADMEStudy",
            "ToxicokineticStudy",
            "BiodistributionStudy",
            "ToxicologyStudy"
          ]
        },
        {
          "name": "ToxicologyStudy",
          "definition": "독성평가를 목적으로 수행된 시험",
          "children": [
            "SingleDoseToxicityStudy",
            "RepeatDoseToxicityStudy",
            "GenotoxicityStudy",
            "CarcinogenicityStudy",
            "ReproductiveToxicityStudy",
            "LocalToleranceStudy",
            "ImmunotoxicityStudy",
            "OtherToxicityStudy"
          ]
        },
        {
          "name": "OtherToxicityStudy",
          "definition": "제품·경로·기전에 따라 필요한 특수독성시험",
          "children": [
            "PhototoxicityStudy",
            "PhotosafetyStudy",
            "SkinSensitizationStudy",
            "JuvenileAnimalStudy",
            "DependenceLiabilityStudy",
            "ImpurityQualificationStudy",
            "CombinationToxicityStudy",
            "MechanisticToxicityStudy",
            "OffTargetStudy",
            "CytokineReleaseStudy",
            "ComplementActivationStudy",
            "ThrombogenicityStudy",
            "TissuePersistenceStudy"
          ]
        },
        {
          "name": "StudyPurpose",
          "definition": "각 시험이 실제로 답해야 하는 과학적 목적",
          "children": [
            "IdentifyAcuteToxicity",
            "IdentifyTargetOrgan",
            "EstablishDoseResponse",
            "EstablishExposureResponse",
            "DetermineNOAEL",
            "DetermineHNSTD",
            "AssessAccumulation",
            "AssessReversibility",
            "AssessVitalOrganFunction",
            "AssessGeneticDamage",
            "AssessCarcinogenicPotential",
            "AssessFertility",
            "AssessEmbryofetalDevelopment",
            "AssessPrePostnatalDevelopment",
            "AssessLocalTissueDamage",
            "AssessImmuneSuppression",
            "AssessImmuneActivation",
            "AssessHypersensitivity",
            "AssessBiodistribution",
            "AssessPersistence",
            "AssessShedding",
            "AssessOnTargetToxicity",
            "AssessOffTargetToxicity"
          ]
        },
        {
          "name": "StudyPurposeAssessment",
          "definition": "적용 가능한 목적별 근거충족 상태",
          "children": [
            "PurposeSupported",
            "PurposePartiallySupported",
            "PurposeUnsupported",
            "PurposeUnknown",
            "PurposeNotApplicableJustified"
          ]
        }
      ],
      "properties": [
        "hasStudyPurpose",
        "addressesToxicityQuestion",
        "supportsClinicalContext",
        "usesTestArticle",
        "hasStudyDesign",
        "generatesObservation",
        "producesFinding",
        "hasApplicabilityStatus",
        "hasPurposeFulfillment",
        "definesNOAEL",
        "definesHNSTD",
        "assessesReversibility",
        "assessesAccumulation"
      ],
      "validation": [
        "시험마다 최소 1개 StudyPurpose 연결",
        "Repeat-dose는 target organ·exposure response·accumulation·reversibility 목적 평가",
        "TK는 독성과 동물노출 연결",
        "시험 존재와 목적충족을 분리"
      ],
      "rules": [
        "Study existence ≠ Study purpose fulfillment",
        "Applicable Purpose 중 근거가 없는 항목은 PurposeUnknown 또는 Unsupported",
        "필수 목적 미충족 → Data Gap 및 다음시험 권고"
      ]
    },
    {
      "id": "study_design",
      "title": "시험설계 및 시험계",
      "subtitle": "Study Design & Test System Ontology",
      "summary": "시험방법이 독성질문과 예정 사람노출에 적절한지를 설계요소별로 검증합니다.",
      "classes": [
        {
          "name": "StudyDesign",
          "definition": "비임상 또는 NAM 시험의 전체 설계",
          "children": [
            "TestSystemDesign",
            "DoseDesign",
            "AdministrationDesign",
            "ObservationDesign",
            "EndpointDesign",
            "RecoveryDesign",
            "TKDesign",
            "StatisticalDesign"
          ]
        },
        {
          "name": "TestSystem",
          "definition": "시험결과의 과학적 관련성을 결정하는 시스템",
          "children": [
            "InSilicoSystem",
            "InVitroSystem",
            "ExVivoSystem",
            "InVivoSystem",
            "RodentSpecies",
            "NonRodentSpecies",
            "DiseaseModel",
            "HumanizedModel",
            "HumanDerivedSystem"
          ]
        },
        {
          "name": "DoseDesign",
          "definition": "용량·농도·노출수준을 설정하는 설계",
          "children": [
            "ControlDose",
            "LowDose",
            "MidDose",
            "HighDose",
            "LimitDose",
            "MTDDose",
            "ExposureBasedDose",
            "ClinicalExposureMatchedDose"
          ]
        },
        {
          "name": "AdministrationDesign",
          "definition": "투여경로·빈도·속도·기간 설계",
          "children": [
            "Route",
            "Frequency",
            "InfusionRate",
            "TreatmentDuration",
            "DoseVolume",
            "FormulationConcentration",
            "DosingInterval"
          ]
        },
        {
          "name": "RecoveryDesign",
          "definition": "가역성·지속성 평가 설계",
          "children": [
            "RecoveryGroup",
            "RecoveryDuration",
            "PostTreatmentObservation",
            "DelayedAssessment"
          ]
        }
      ],
      "properties": [
        "hasSpecies",
        "hasStrain",
        "hasSex",
        "hasAge",
        "hasDiseaseStatus",
        "hasTargetExpression",
        "hasPharmacologicalRelevance",
        "hasMetabolicRelevance",
        "hasSequenceHomology",
        "hasImmuneSystemRelevance",
        "producesExposure",
        "causesFinding",
        "coversHumanExposure",
        "showsDoseResponse",
        "hasRecoveryDuration",
        "hasInfusionRate"
      ],
      "validation": [
        "Study route와 clinical route 비교",
        "Study duration과 planned treatment duration 비교",
        "동물 또는 NAM exposure가 예정 사람노출을 커버하는지 확인",
        "음성결과에 target exposure와 valid controls 필수"
      ],
      "rules": [
        "Route mismatch → RouteMismatch Gap",
        "Duration mismatch → DurationMismatch Gap",
        "Missing recovery design → 가역성 Unknown",
        "Insufficient exposure → 음성결과 신뢰 제한"
      ]
    },
    {
      "id": "ai",
      "title": "AI 모델 및 적용범위",
      "subtitle": "AI Model Card Ontology",
      "summary": "모델 성능과 현재 후보에서의 사용 가능성을 분리합니다.",
      "classes": [
        {
          "name": "AIModel",
          "definition": "특정 독성 endpoint를 예측하는 계산모델",
          "children": [
            "RuleBasedQSAR",
            "StatisticalQSAR",
            "MachineLearningClassifier",
            "MachineLearningRegressor",
            "DeepLearningModel",
            "GraphNeuralNetwork",
            "TranscriptomicSignatureModel",
            "NetworkToxicologyModel"
          ]
        },
        {
          "name": "AIDataset",
          "definition": "모델 개발·검증에 사용된 데이터",
          "children": [
            "TrainingDataset",
            "TuningDataset",
            "InternalTestDataset",
            "ExternalValidationDataset",
            "ProspectiveValidationDataset"
          ]
        },
        {
          "name": "PerformanceMetricMeasurement",
          "definition": "특정 threshold와 dataset에서 측정된 성능",
          "children": [
            "SensitivityMeasurement",
            "SpecificityMeasurement",
            "PositivePredictiveValueMeasurement",
            "NegativePredictiveValueMeasurement",
            "FalsePositiveRateMeasurement",
            "FalseNegativeRateMeasurement",
            "AccuracyMeasurement",
            "BalancedAccuracyMeasurement",
            "AUROCMeasurement",
            "AUPRCMeasurement",
            "BrierScoreMeasurement",
            "CalibrationSlopeMeasurement",
            "CalibrationInterceptMeasurement"
          ]
        },
        {
          "name": "ApplicabilityDomain",
          "definition": "모델이 신뢰 가능하게 사용될 수 있는 범위",
          "children": [
            "ChemicalApplicabilityDomain",
            "StructuralApplicabilityDomain",
            "BiologicalApplicabilityDomain",
            "ModalityApplicabilityDomain",
            "MechanisticApplicabilityDomain",
            "ExposureApplicabilityDomain",
            "PopulationApplicabilityDomain",
            "EndpointApplicabilityDomain"
          ]
        }
      ],
      "properties": [
        "hasModelName",
        "hasModelVersion",
        "hasArchitecture",
        "hasIntendedEndpoint",
        "hasInputDefinition",
        "hasOutputDefinition",
        "hasDecisionThreshold",
        "hasTrainingDataset",
        "hasExternalValidationDataset",
        "hasReferenceStandard",
        "hasApplicabilityDomain",
        "hasPerformanceMetric",
        "hasKnownLimitation",
        "hasChangeControlPlan",
        "hasLifecycleMonitoringPlan"
      ],
      "validation": [
        "모델명·버전·endpoint 필수",
        "음성예측은 sensitivity 및 false-negative 정보 필요",
        "학습·검증 데이터의 modality와 독립성 기술",
        "applicability domain과 후보 domain status 필수"
      ],
      "rules": [
        "Out-of-domain negative → Reliable Negative 불인정, 최대 R1",
        "False-negative 성능 미상 + 중대 결정 → 최대 R2",
        "Endpoint mismatch → R0",
        "Test dataset가 training dataset와 겹침 → 외부검증 부적절"
      ]
    },
    {
      "id": "nam",
      "title": "NAM 시험계 및 실행 유효성",
      "subtitle": "NAM Assay Ontology",
      "summary": "사람 유래 여부뿐 아니라 관련 세포, 기능, 대조군, 반복노출과 플랫폼 상호작용을 평가합니다.",
      "classes": [
        {
          "name": "InVitroNAM",
          "definition": "비동물 기반 시험법",
          "children": [
            "TwoDimensionalCellAssay",
            "CocultureAssay",
            "ThreeDimensionalSpheroid",
            "OrganoidAssay",
            "OrganOnChip",
            "MicrophysiologicalSystem",
            "HighContentImagingAssay",
            "OmicsBasedAssay",
            "ReporterGeneAssay",
            "FunctionalCellAssay"
          ]
        },
        {
          "name": "TestSystem",
          "definition": "시험에 사용된 생물학적 시스템",
          "children": [
            "HumanDerivedSystem",
            "AnimalDerivedSystem",
            "PrimaryCellSystem",
            "ImmortalizedCellSystem",
            "StemCellDerivedSystem",
            "CocultureSystem",
            "SpheroidSystem",
            "OrganoidSystem",
            "OrganChipSystem"
          ]
        },
        {
          "name": "LiverCellType",
          "definition": "간독성 사람 관련성의 주요 세포",
          "children": [
            "PrimaryHumanHepatocyte",
            "iPSCDerivedHepatocyte",
            "KupfferCell",
            "HepaticStellateCell",
            "LiverSinusoidalEndothelialCell",
            "Cholangiocyte",
            "HepaticImmuneCell"
          ]
        },
        {
          "name": "AssayControl",
          "definition": "시험실행 유효성과 독성기여도 분리를 위한 대조군",
          "children": [
            "PositiveControl",
            "NegativeControl",
            "VehicleControl",
            "UntreatedControl",
            "CarrierOnlyControl",
            "ActiveOnlyControl",
            "FormulationMatchedControl",
            "PlatformMaterialControl",
            "ReferenceCompoundControl"
          ]
        },
        {
          "name": "PlatformInteractionAssessment",
          "definition": "시험물질과 chip·matrix·배지의 상호작용",
          "children": [
            "TestArticleAdsorption",
            "TestArticleAbsorption",
            "MatrixBinding",
            "DeviceLeaching",
            "MaterialInducedToxicity",
            "SurfaceLoss",
            "AggregationInMedium",
            "Sedimentation",
            "FlowDependentDistribution"
          ]
        }
      ],
      "properties": [
        "hasMethodVersion",
        "hasProtocol",
        "hasSOP",
        "hasQualitySystem",
        "hasTestSystem",
        "hasExposureDesign",
        "hasEndpoint",
        "hasControl",
        "hasReferenceCompound",
        "hasAcceptanceCriterion",
        "hasStatisticalMethod",
        "hasReproducibilityEvidence",
        "hasKnownLimitation",
        "hasCellType",
        "hasMetabolicCompetence",
        "hasImmuneCompetence"
      ],
      "validation": [
        "양성·음성대조군 필수",
        "Negative NAM은 적절한 target exposure 입증 필요",
        "반복 사람노출은 반복 NAM 또는 bridging rationale 필요",
        "나노의약품은 carrier-only control 및 platform interaction 평가 필요"
      ],
      "rules": [
        "Positive 또는 Negative control 실패 → 실행 무효",
        "NAM 음성 + 실제 노출 미측정 → Unreliable Negative",
        "Repeat clinical exposure + acute NAM → 최대 R2",
        "Carrier-only control 누락 → formulation contribution 평가 불가"
      ]
    },
    {
      "id": "exposure",
      "title": "노출 및 사람 번역",
      "subtitle": "Exposure & Translation Ontology",
      "summary": "명목 농도를 실제 세포·조직·사람 노출로 연결합니다.",
      "classes": [
        {
          "name": "ExposureContext",
          "definition": "계획 또는 관찰된 노출 맥락",
          "children": [
            "PlannedHumanExposure",
            "ObservedHumanExposure",
            "InVivoExposure",
            "InVitroExposure",
            "TissueExposure",
            "IntracellularExposure"
          ]
        },
        {
          "name": "ExposureMetric",
          "definition": "노출을 정량화하는 지표",
          "children": [
            "AdministeredDose",
            "NominalConcentration",
            "MeasuredTotalConcentration",
            "UnboundConcentration",
            "IntracellularConcentration",
            "TargetTissueConcentration",
            "Cmax",
            "Cmin",
            "AUC",
            "HalfLife",
            "AccumulationRatio",
            "TimeAboveThreshold",
            "ExposureMargin"
          ]
        },
        {
          "name": "ExposureDesign",
          "definition": "노출의 시간적 설계",
          "children": [
            "SingleExposure",
            "RepeatedExposure",
            "ContinuousExposure",
            "PulseExposure",
            "RecoveryExposure",
            "WashoutDesign"
          ]
        },
        {
          "name": "ExposureTranslationModel",
          "definition": "in vitro 결과를 사람노출로 번역하는 모델",
          "children": [
            "SimpleConcentrationBridge",
            "ProteinBindingAdjustedBridge",
            "FreeConcentrationBridge",
            "QIVIVEModel",
            "PBPKModel",
            "TissuePartitionModel",
            "IntracellularExposureModel"
          ]
        }
      ],
      "properties": [
        "hasNominalConcentration",
        "hasMeasuredConcentration",
        "hasUnboundConcentration",
        "hasIntracellularConcentration",
        "coversPlannedHumanCmax",
        "coversPlannedHumanAUC",
        "coversTreatmentDuration",
        "showsAccumulation",
        "hasExposureMargin",
        "translatedBy",
        "hasTargetTissueConcentration"
      ],
      "validation": [
        "수치는 값·단위·시간·노출형태와 함께 저장",
        "Negative NAM은 충분한 target exposure 확인",
        "계획 임상기간과 NAM 노출기간 비교",
        "QIVIVE/PBPK의 가정과 불확실성 기록"
      ],
      "rules": [
        "Nominal concentration ≠ target exposure",
        "사람 Cmax/AUC 연결 없음 → exposure relevance 제한",
        "정량 biodistribution 없음 → 나노의약품 간·비장 위험 미해결"
      ]
    },
    {
      "id": "evidence",
      "title": "근거·Assertion·Provenance",
      "subtitle": "Evidence Ontology",
      "summary": "문서 자체와 문서에서 추출된 주장을 분리하고 모든 결론을 출처에 연결합니다.",
      "classes": [
        {
          "name": "EvidenceItem",
          "definition": "보고서, 논문, 표, 원자료 등 근거",
          "children": [
            "AIModelCard",
            "AIValidationReport",
            "DatasetDescription",
            "SoftwareVerificationReport",
            "NAMProtocol",
            "NAMStudyReport",
            "RawData",
            "DataTable",
            "Figure",
            "Publication",
            "ProductCharacterizationReport",
            "BiodistributionReport",
            "PKTKReport",
            "QIVIVEReport",
            "RegulatoryGuidance",
            "RegulatoryCorrespondence",
            "ExpertJudgment",
            "PriorClassKnowledge"
          ]
        },
        {
          "name": "EvidenceAssertion",
          "definition": "근거로부터 추출된 구조화된 주장",
          "children": [
            "ProposedAssertion",
            "AcceptedAssertion",
            "CorrectedAssertion",
            "RejectedAssertion",
            "SupersededAssertion"
          ]
        },
        {
          "name": "PredictionResult",
          "definition": "AI 또는 in silico 방법이 생성한 예측",
          "children": [
            "BinaryPrediction",
            "MulticlassPrediction",
            "ProbabilityPrediction",
            "ContinuousPrediction",
            "RankedPrediction",
            "MechanisticPrediction"
          ]
        },
        {
          "name": "Observation",
          "definition": "시험에서 실제 측정된 값",
          "children": [
            "QuantitativeObservation",
            "QualitativeObservation",
            "ImagingObservation",
            "OmicsObservation",
            "FunctionalObservation",
            "ClinicalBiomarkerObservation"
          ]
        },
        {
          "name": "ToxicityFinding",
          "definition": "Observation을 과학적으로 해석한 소견",
          "children": [
            "PredictedToxicitySignal",
            "NAMToxicityFinding",
            "InVivoToxicityFinding",
            "ClinicalToxicityFinding",
            "IntegratedToxicityFinding"
          ]
        },
        {
          "name": "ResultReliability",
          "definition": "결과의 해석가능성과 신뢰성",
          "children": [
            "ReliablePositive",
            "ReliableNegative",
            "ProvisionallyReliable",
            "UnreliablePositive",
            "UnreliableNegative",
            "UninterpretableResult"
          ]
        }
      ],
      "properties": [
        "hasSubject",
        "hasPredicate",
        "hasObject",
        "supportedByEvidence",
        "contradictedByEvidence",
        "hasSourceLocation",
        "extractedBy",
        "hasExtractionConfidence",
        "hasReviewStatus",
        "reviewedBy",
        "derivedFrom",
        "reportedIn",
        "usesBatch",
        "basedOnObservation",
        "generatedByExecution"
      ],
      "validation": [
        "Accepted Assertion은 출처·위치·검토자·버전 필수",
        "AI 추출은 Proposed로 시작",
        "Prediction·Observation·Finding 분리",
        "Missing Evidence를 Negative로 변환 금지"
      ],
      "rules": [
        "승인·수정된 Assertion만 고영향 평가에 사용",
        "Untraceable Evidence → R4/R5 제한",
        "Negative Finding은 exposure·controls·acceptance criteria 충족 시에만 Reliable Negative"
      ]
    },
    {
      "id": "human_risk",
      "title": "독성소견·사람 관련성·위험",
      "subtitle": "Finding & Human Risk Ontology",
      "summary": "측정값, 독성소견, 사람 관련성 및 실제 사람 위험을 서로 다른 객체로 유지합니다.",
      "classes": [
        {
          "name": "ToxicityFinding",
          "definition": "시험에서 관찰된 결과의 과학적 독성 해석",
          "children": [
            "ClinicalObservationFinding",
            "MortalityFinding",
            "BodyWeightFinding",
            "FoodConsumptionFinding",
            "HematologyFinding",
            "ClinicalChemistryFinding",
            "UrinalysisFinding",
            "ECGFinding",
            "OrganWeightFinding",
            "MacroscopicFinding",
            "HistopathologyFinding",
            "ImmuneFinding",
            "GeneticToxicityFinding",
            "LocalToleranceFinding"
          ]
        },
        {
          "name": "FindingAssessment",
          "definition": "Finding의 심각도·유해성·인과성·가역성 평가",
          "children": [
            "SeverityAssessment",
            "AdversityAssessment",
            "CausalityAssessment",
            "ReversibilityAssessment",
            "BiologicalSignificanceAssessment",
            "StatisticalSignificanceAssessment"
          ]
        },
        {
          "name": "HumanRelevanceAssessment",
          "definition": "동물·NAM·AI 소견의 사람 관련성 평가",
          "children": [
            "HighHumanRelevance",
            "ModerateHumanRelevance",
            "LowHumanRelevance",
            "HumanSpecificRisk",
            "AnimalSpecificFinding",
            "UnknownHumanRelevance"
          ]
        },
        {
          "name": "RelevanceFactor",
          "definition": "사람 관련성 결론을 지지하는 요인",
          "children": [
            "TargetConservation",
            "SequenceHomology",
            "ReceptorExpression",
            "MetabolicSimilarity",
            "ExposureSimilarity",
            "AnatomicalSimilarity",
            "ImmuneSimilarity",
            "MechanisticPlausibility",
            "ClinicalClassEffect",
            "HumanInVitroEvidence"
          ]
        },
        {
          "name": "HumanRisk",
          "definition": "Hazard와 Finding을 노출·사람 관련성과 함께 해석한 개발위험",
          "children": [
            "IdentifiedHumanRisk",
            "PotentialHumanRisk",
            "MitigatedHumanRisk",
            "UnresolvedHumanRisk",
            "UnknownHumanRisk"
          ]
        }
      ],
      "properties": [
        "hasEndpoint",
        "hasObservedValue",
        "hasReferenceRange",
        "hasIncidence",
        "hasSeverity",
        "hasOnset",
        "hasDuration",
        "hasDose",
        "hasExposure",
        "hasSex",
        "hasSpecies",
        "hasTargetOrgan",
        "hasDoseResponse",
        "hasExposureResponse",
        "hasReversibility",
        "hasAdversityAssessment",
        "hasCausalityAssessment",
        "hasHumanRelevance",
        "hasRelevanceFactor",
        "determinesHumanRisk"
      ],
      "validation": [
        "Observation과 Finding 분리",
        "Human relevance 결론마다 factor와 evidence 필수",
        "rat-specific 주장만으로 Low relevance 불가",
        "Negative Finding과 No Human Risk 분리"
      ],
      "rules": [
        "On-target mechanism + human target expression + overlapping exposure → High relevance 가능",
        "Species-specific pathway가 사람에 없고 기전이 실험적으로 확인된 경우에만 Low relevance",
        "Severe irreversible finding at planned exposure + high relevance → 개발 중대위험"
      ]
    },
    {
      "id": "assessment",
      "title": "Evidence Assurance 평가",
      "subtitle": "Assessment Ontology",
      "summary": "하나의 점수 대신 서로 다른 신뢰 문제를 여섯 축으로 평가합니다.",
      "classes": [
        {
          "name": "MethodCredibilityAssessment",
          "definition": "방법 자체의 신뢰성",
          "children": [
            "MethodIdentityAssessment",
            "DocumentationCompletenessAssessment",
            "DataQualityAssessment",
            "ModelPerformanceAssessment",
            "ExternalValidationAssessment",
            "ReproducibilityAssessment",
            "SoftwareVerificationAssessment",
            "ReferenceStandardAssessment",
            "QualitySystemAssessment",
            "ChangeControlAssessment",
            "LifecycleManagementAssessment"
          ]
        },
        {
          "name": "CandidateApplicabilityAssessment",
          "definition": "현재 후보에 대한 적용성",
          "children": [
            "ChemicalDomainFitAssessment",
            "StructuralDomainFitAssessment",
            "ModalityDomainFitAssessment",
            "MechanisticDomainFitAssessment",
            "RouteDomainFitAssessment",
            "ExposureDomainFitAssessment",
            "EndpointDomainFitAssessment",
            "PopulationDomainFitAssessment"
          ]
        },
        {
          "name": "HumanBiologicalRelevanceAssessment",
          "definition": "사람 생물학·기전 관련성",
          "children": [
            "SpeciesOriginAssessment",
            "CellTypeRelevanceAssessment",
            "TissueArchitectureAssessment",
            "PhysiologicalFunctionAssessment",
            "MetabolicCompetenceAssessment",
            "ImmuneCompetenceAssessment",
            "MechanisticAlignmentAssessment",
            "DonorRepresentationAssessment",
            "ClinicalEndpointLinkageAssessment"
          ]
        },
        {
          "name": "ExposureRelevanceAssessment",
          "definition": "시험과 예정 사람노출의 관련성",
          "children": [
            "NominalExposureAssessment",
            "FreeExposureAssessment",
            "IntracellularExposureAssessment",
            "TargetTissueExposureAssessment",
            "CmaxCoverageAssessment",
            "AUCCoverageAssessment",
            "RepeatedExposureCoverageAssessment",
            "AccumulationAssessment",
            "QIVIVEAdequacyAssessment"
          ]
        },
        {
          "name": "EvidenceConcordanceAssessment",
          "definition": "근거 흐름의 일치와 상충",
          "children": [
            "DirectionalConcordance",
            "MechanisticConcordance",
            "DoseResponseConcordance",
            "ExposureConcordance",
            "TemporalConcordance",
            "CrossPlatformConcordance",
            "HumanAnimalConcordance"
          ]
        },
        {
          "name": "FitForPurposeAssessment",
          "definition": "정의된 COU에서의 최종 적합성",
          "children": [
            "COUAdequacyAssessment",
            "PerformanceAdequacyAssessment",
            "EvidenceSufficiencyAssessment",
            "ResidualRiskAssessment",
            "DecisionUseAdequacyAssessment"
          ]
        }
      ],
      "properties": [
        "assessesEntity",
        "hasAssessmentDimension",
        "hasAssessmentLevel",
        "hasNumericScore",
        "hasConclusion",
        "hasRationale",
        "supportedByEvidence",
        "generatedByRule",
        "hasUncertainty",
        "reviewedBy",
        "hasAssessmentDate"
      ],
      "validation": [
        "Unknown과 0을 구분",
        "각 점수에 근거·rule version·평가일 연결",
        "평균점수로 Hard Gate를 보상하지 않음"
      ],
      "rules": [
        "Method credibility가 높아도 applicability가 낮으면 Evidence Role 제한",
        "Human relevance와 exposure relevance 미충족 시 R4/R5 불가",
        "AI/NAM 상충 → 최대 R2 및 Expert Review"
      ]
    },
    {
      "id": "gaps",
      "title": "Data Gap 및 잔여 불확실성",
      "subtitle": "Gap & Uncertainty Ontology",
      "summary": "자료 부족과 낮은 독성우려를 분리하고, 해결해야 할 다음 근거를 지정합니다.",
      "classes": [
        {
          "name": "ResidualUncertainty",
          "definition": "평가 후에도 남아 있는 불확실성",
          "children": [
            "DataUncertainty",
            "ModelUncertainty",
            "AssayUncertainty",
            "ApplicabilityUncertainty",
            "ProductUncertainty",
            "ExposureUncertainty",
            "TranslationUncertainty",
            "MechanisticUncertainty",
            "BiologicalVariability",
            "EvidenceConflictUncertainty",
            "DecisionUncertainty",
            "RegulatoryUncertainty"
          ]
        },
        {
          "name": "DataGap",
          "definition": "필요한 질문에 답할 근거가 없거나 해석 불가능한 상태",
          "children": [
            "MissingQuestionOfInterest",
            "MissingContextOfUse",
            "EndpointMismatch",
            "MissingMethodIdentity",
            "MissingModelVersion",
            "MissingDatasetDescription",
            "MissingExternalValidation",
            "NonIndependentTestDataset",
            "UnknownFalseNegativePerformance",
            "MissingDecisionThreshold",
            "MissingApplicabilityDomain",
            "OutOfDomainPrediction",
            "MissingNAMProtocol",
            "MissingAcceptanceCriterion",
            "InvalidControl",
            "MissingReferenceCompound",
            "MissingReproducibilityEvidence",
            "MissingDonorVariability",
            "MissingHumanRelevantCellType",
            "MissingMetabolicCompetence",
            "MissingImmuneCompetence",
            "MissingMeasuredExposure",
            "MissingFreeConcentration",
            "MissingIntracellularExposure",
            "AcuteRepeatExposureMismatch",
            "MissingQIVIVE",
            "MissingBiodistribution",
            "MissingCarrierOnlyControl",
            "MissingActiveOnlyControl",
            "PlatformInteractionUnknown",
            "UnresolvedConflictingEvidence",
            "MissingTraceability",
            "MissingExpertReview",
            "SupersededMethodVersion"
          ]
        },
        {
          "name": "GapCriticality",
          "definition": "의사결정에 미치는 심각도",
          "children": [
            "Informational",
            "Minor",
            "Major",
            "Critical",
            "DecisionBlocking"
          ]
        },
        {
          "name": "GapResolutionPlan",
          "definition": "Gap을 해소할 구체적인 다음 행동",
          "children": [
            "AdditionalAIValidation",
            "OrthogonalNAM",
            "RepeatedExposureNAM",
            "QIVIVEAnalysis",
            "PBPKAnalysis",
            "BiodistributionStudy",
            "CarrierControlStudy",
            "MechanisticStudy",
            "TargetedInVivoStudy",
            "ExpertEscalation",
            "RegulatoryMeeting"
          ]
        }
      ],
      "properties": [
        "hasUncertaintySource",
        "hasMagnitude",
        "hasPatientSafetyImpact",
        "hasDecisionImpact",
        "canBeReducedBy",
        "hasResolutionPriority",
        "hasCriticality",
        "hasRequiredTiming",
        "recommendsMethod",
        "requiresEvidence",
        "hasOwner",
        "hasDependency",
        "affectsDecision",
        "limitsEvidenceRole"
      ],
      "validation": [
        "Gap마다 criticality·timing·decision impact 필수",
        "Missing과 Not Applicable 분리",
        "해결계획은 owner와 evidence requirement 포함"
      ],
      "rules": [
        "Critical gap 존재 → 낮은 concern 분류 불가",
        "Decision-blocking gap → 최대 Evidence Role 제한",
        "Missing evidence → Unknown + DataGap 생성"
      ]
    },
    {
      "id": "clinical",
      "title": "임상 번역 및 규제 자문",
      "subtitle": "Clinical Translation & Regulatory Decision Ontology",
      "summary": "독성근거를 임상 용량·모니터링·중단기준과 다음 개발단계 권고로 연결합니다.",
      "classes": [
        {
          "name": "ClinicalTrialContext",
          "definition": "비임상 패키지가 지원해야 하는 임상시험 조건",
          "children": [
            "TrialPopulation",
            "DosePlan",
            "RoutePlan",
            "TreatmentDuration",
            "DoseEscalationPlan",
            "ClinicalMonitoringPlan",
            "EligibilityPlan",
            "StoppingRulePlan",
            "FollowUpPlan"
          ]
        },
        {
          "name": "ClinicalMitigation",
          "definition": "임상시험에 적용하는 위험완화조치",
          "children": [
            "StartingDoseSelection",
            "MaximumDoseLimit",
            "DoseEscalationRestriction",
            "SentinelDosing",
            "StaggeredEnrollment",
            "ObservationPeriod",
            "LaboratoryMonitoring",
            "BiomarkerMonitoring",
            "ECGMonitoring",
            "InfusionRateControl",
            "Premedication",
            "EligibilityCriterion",
            "StoppingRule",
            "FollowUpRequirement",
            "EmergencyManagement"
          ]
        },
        {
          "name": "AdvisoryAssessment",
          "definition": "규제결정을 대체하지 않는 설명 가능한 자문",
          "children": [
            "EvidenceCoverageAssessment",
            "EvidenceConfidenceAssessment",
            "ToxicityConcernAssessment",
            "StudyDesignAssessment",
            "RegulatoryRelevanceAssessment",
            "DevelopmentReadinessAssessment"
          ]
        },
        {
          "name": "AdvisoryRecommendation",
          "definition": "다음 개발단계에 대한 조건부 권고",
          "children": [
            "StudyRecommendation",
            "DataRecommendation",
            "MonitoringRecommendation",
            "DoseRecommendation",
            "CMCComparabilityRecommendation",
            "RegulatoryMeetingRecommendation",
            "ExpertEscalationRecommendation"
          ]
        },
        {
          "name": "RegulatoryDecision",
          "definition": "내부 규제논리를 표현하는 최종 상태",
          "children": [
            "Go",
            "ConditionalGo",
            "Hold",
            "NoGo",
            "UnableToAssess"
          ]
        },
        {
          "name": "CriticalGate",
          "definition": "현재 임상진입 지원 여부를 제한하는 핵심 Gate",
          "children": [
            "FinalTestArticleDefinedGate",
            "TestArticleComparabilityGate",
            "RepeatDoseCoverageGate",
            "ExposureCoverageGate",
            "RouteCoverageGate",
            "RecoveryAssessmentGate",
            "StartingDoseJustificationGate",
            "ClinicalMonitoringGate"
          ]
        }
      ],
      "properties": [
        "hasPopulation",
        "hasStartingDose",
        "hasMaximumPlannedDose",
        "hasClinicalRoute",
        "hasFrequency",
        "hasTreatmentDuration",
        "hasSentinelDesign",
        "hasEscalationInterval",
        "hasFollowUpDuration",
        "requiresMonitoring",
        "limitsStartingDose",
        "limitsMaximumDose",
        "requiresStoppingRule",
        "requiresEligibilityRestriction",
        "requiresFollowUp",
        "isMitigatedBy",
        "hasAdvisoryStatus",
        "hasRecommendationPriority",
        "supportsClinicalEntry"
      ],
      "validation": [
        "독성소견이 임상 모니터링·용량·중단기준 중 관련 항목과 연결",
        "starting dose justification 필수",
        "critical gap과 clinical mitigation 상태 확인",
        "자동결론과 Human Expert Decision 분리"
      ],
      "rules": [
        "Missing repeat-dose study가 현재 단계에 필수 → Additional Evidence Required / Development Hold",
        "TK missing + systemic exposure required → Exposure Gate 실패",
        "Critical gap 존재 → 자동 최대 권고 제한",
        "NORA는 규제기관 승인 여부를 보장하지 않음"
      ]
    },
    {
      "id": "action",
      "title": "Evidence Role 및 3Rs 권고",
      "subtitle": "Action Ontology",
      "summary": "근거의 사용 가능한 역할과 동물실험 보완·정교화·축소·대체후보를 명확히 구분합니다.",
      "classes": [
        {
          "name": "EvidenceRole",
          "definition": "현재 근거를 어디까지 사용할 수 있는지 나타내는 통제어휘",
          "children": [
            "R0_NotAssessable",
            "R1_HypothesisGenerating",
            "R2_ScreeningUse",
            "R3_SupportiveEvidence",
            "R4_ReductionSupporting",
            "R5_ReplacementCandidate"
          ]
        },
        {
          "name": "AnimalUseRecommendation",
          "definition": "동물사용과 관련된 권고",
          "children": [
            "NoAnimalUseConclusion",
            "NoReductionSupported",
            "RefinementRecommended",
            "ReductionPotentialIdentified",
            "ReductionSupported",
            "ReplacementCandidateIdentified",
            "AgencyDiscussionRequired",
            "UnableToAssessAnimalUse"
          ]
        },
        {
          "name": "ThreeRsAction",
          "definition": "Refinement·Reduction·Replacement 조치",
          "children": [
            "RefineEndpointSelection",
            "RefineSamplingTime",
            "RefineDoseSelection",
            "RefineMonitoring",
            "ReduceAnimalNumber",
            "ReduceDoseGroup",
            "ReduceSpecies",
            "ReduceStudyDuration",
            "ReduceStandaloneStudy",
            "IntegrateEndpointIntoExistingStudy",
            "ReplaceSpecificEndpoint",
            "ReplaceSpecificMechanisticQuestion",
            "ReplaceSpecificAnimalSpecies",
            "ReplaceSpecificStudyCandidate"
          ]
        },
        {
          "name": "AdvisoryRecommendation",
          "definition": "다음 근거와 조치를 설명하는 자문",
          "children": [
            "AdditionalAIValidationRecommendation",
            "ApplicabilityDomainExtensionRecommendation",
            "OrthogonalNAMRecommendation",
            "RepeatedExposureRecommendation",
            "QIVIVERecommendation",
            "PBPKRecommendation",
            "BiodistributionRecommendation",
            "CarrierControlRecommendation",
            "MechanisticStudyRecommendation",
            "TargetedInVivoRecommendation",
            "ExpertEscalationRecommendation",
            "RegulatoryMeetingRecommendation"
          ]
        }
      ],
      "properties": [
        "assignsEvidenceRole",
        "supportsAnimalUseAction",
        "hasReplacementTarget",
        "hasReductionTarget",
        "hasAffectedSpecies",
        "hasAffectedEndpoint",
        "hasAffectedDoseGroup",
        "hasAffectedStudy",
        "hasConditions",
        "requiresExpertApproval",
        "requiresAgencyDiscussion",
        "hasObservationStatement",
        "hasInterpretationStatement",
        "hasDevelopmentRelevanceStatement",
        "hasRecommendedAction"
      ],
      "validation": [
        "R4/R5는 전문가 검토 필수",
        "R5는 좁게 정의된 COU 필수",
        "Replacement target은 endpoint·species·study 수준으로 명시",
        "전체 안전성 또는 전체 독성패키지 대체 표현 금지"
      ],
      "rules": [
        "핵심 평가축 ≥3 + 독립근거 ≥2 + critical gap 없음 + 전문가 승인 → R4 가능",
        "R4 + 외부검증 + false-negative 허용 + 재현성 + 좁은 COU → R5 후보",
        "R5 ≠ 규제 qualification 또는 면제"
      ]
    },
    {
      "id": "governance",
      "title": "전문가 검토 및 감사 추적",
      "subtitle": "Human-in-the-loop Governance",
      "summary": "누가 어떤 근거와 규칙으로 결론을 만들고 변경했는지 기록합니다.",
      "classes": [
        {
          "name": "Agent",
          "definition": "평가·검토·결정에 참여하는 주체",
          "children": [
            "Sponsor",
            "ModelDeveloper",
            "NAMDeveloper",
            "TestingLaboratory",
            "DataScientist",
            "Toxicologist",
            "Pathologist",
            "Pharmacokineticist",
            "RegulatoryScientist",
            "QualityReviewer",
            "DecisionOwner"
          ]
        },
        {
          "name": "ExpertReview",
          "definition": "자동평가에 대한 사람의 검토",
          "children": [
            "Accept",
            "AcceptWithCondition",
            "Correct",
            "Reject",
            "Escalate",
            "Override"
          ]
        },
        {
          "name": "OverrideRecord",
          "definition": "자동결론을 변경한 과학적 기록",
          "children": [
            "OriginalConclusion",
            "RevisedConclusion",
            "ScientificRationale",
            "AdditionalEvidence"
          ]
        },
        {
          "name": "AssessmentRun",
          "definition": "한 번의 NORA 평가 전체 기록",
          "children": [
            "InputSnapshot",
            "RuleExecutionSet",
            "AssessmentResult",
            "RecommendationSet",
            "AuditEvent"
          ]
        },
        {
          "name": "RuleExecution",
          "definition": "특정 규칙이 어떤 사실에 적용되어 어떤 결과를 생성했는지 기록",
          "children": [
            "TriggeredRule",
            "NonTriggeredRule",
            "RuleException",
            "RuleOverride"
          ]
        }
      ],
      "properties": [
        "hasReviewer",
        "reviewsAssessment",
        "hasReviewAction",
        "hasReviewRationale",
        "hasReviewDate",
        "hasConflictOfInterestStatement",
        "hasSignature",
        "overridesAutomatedConclusion",
        "hasOriginalConclusion",
        "hasRevisedConclusion",
        "hasScientificRationale",
        "performedBy",
        "approvedBy",
        "usesOntologyVersion",
        "usesRuleSetVersion",
        "usesModelVersion",
        "usesNAMMethodVersion",
        "usesInputSnapshot",
        "hasInputHash",
        "hasExecutionTimestamp",
        "generatesAssessment",
        "generatesRecommendation",
        "hasAuditStatus"
      ],
      "validation": [
        "모든 AssessmentRun에 ontology·rule·method version 필수",
        "Override는 원결론·수정결론·근거·승인자 필수",
        "모델 또는 시험법 version 변경 시 reassessment flag"
      ],
      "rules": [
        "R4/R5에 Expert Review가 없으면 최대 R3",
        "Superseded version 사용 → ReassessmentRequired",
        "승인되지 않은 Assertion은 고영향 규칙 입력에서 제외"
      ]
    }
  ],
  "roles": [
    {
      "code": "R0",
      "name": "평가 불가",
      "description": "필수정보 또는 유효한 근거가 부족하여 사용 가능한 역할을 정할 수 없음",
      "animalUse": "동물사용 변경 결론 불가"
    },
    {
      "code": "R1",
      "name": "가설 생성",
      "description": "잠재 위험이나 기전을 제안하는 수준",
      "animalUse": "축소·대체 미지원"
    },
    {
      "code": "R2",
      "name": "초기 선별",
      "description": "후보 우선순위 및 추가시험 선택에 사용 가능",
      "animalUse": "축소·대체 미지원"
    },
    {
      "code": "R3",
      "name": "보조 근거",
      "description": "다른 독립적 근거와 함께 독성판단을 지원",
      "animalUse": "시험 정교화 가능, 축소는 추가검토"
    },
    {
      "code": "R4",
      "name": "동물시험 축소 지원",
      "description": "특정 동물 수·용량군·endpoint 축소를 제한적으로 지원",
      "animalUse": "명시된 조건 아래 축소 검토"
    },
    {
      "code": "R5",
      "name": "특정 시험 대체 후보",
      "description": "좁게 정의된 COU에서 특정 endpoint 대체를 공식 검토할 후보",
      "animalUse": "규제기관 논의·qualification 필요"
    }
  ],
  "competencyQuestions": [
    "현재 AI 결과는 어떤 Question of Interest와 Context of Use를 지원하는가?",
    "AI 모델은 현재 후보물질의 modality와 화학적 범위를 포함하는가?",
    "음성 예측의 false-negative 성능은 현재 endpoint와 COU에서 알려져 있는가?",
    "이번 NAM 실행은 대조군과 acceptance criteria를 충족했는가?",
    "시험에서 실제 target-site exposure가 입증되었는가?",
    "반복 임상노출이 단회 NAM 시험으로 충분히 지원되는가?",
    "사용한 간 모델은 필요한 세포와 기능을 포함하는가?",
    "AI, NAM, class evidence가 서로 일치하는가?",
    "어떤 Data Gap이 Evidence Role을 제한하는가?",
    "R4 또는 R5를 위해 부족한 근거는 무엇인가?",
    "어떤 동물시험 요소를 줄일 수 있고 어떤 요소는 유지해야 하는가?",
    "각 권고는 어느 문서의 어느 페이지·표에 근거하는가?",
    "어떤 규칙 버전이 현재 결론을 생성했는가?",
    "전문가가 자동결론을 변경했는가? 그 이유는 무엇인가?",
    "모델이나 시험법 버전이 변경되면 어떤 평가를 다시 수행해야 하는가?"
  ]
};
