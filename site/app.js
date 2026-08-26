(() => {
  const ontology = window.NORA_ONTOLOGY;
  const gp = window.NORA_GP_L_CT;
  const EVIDENCE_ROLE_RANGE = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5'];
  if (!ontology) return;

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const esc = (value) => String(value ?? '').replace(/[&<>'"]/g, (ch) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[ch]));

  // Header / mobile
  const menu = $('#mobileMenu');
  const nav = $('#mainNav');
  menu?.addEventListener('click', () => {
    const opened = nav.classList.toggle('open');
    menu.setAttribute('aria-expanded', String(opened));
  });
  $$('#mainNav a').forEach((link) => link.addEventListener('click', () => nav.classList.remove('open')));

  // Modal
  $$('[data-open-modal]').forEach((button) => button.addEventListener('click', () => {
    const modal = document.getElementById(button.dataset.openModal);
    modal?.classList.add('open');
    modal?.querySelector('[data-close-modal]')?.focus();
  }));
  $$('[data-close-modal]').forEach((button) => button.addEventListener('click', () => button.closest('.modal')?.classList.remove('open')));
  $$('.modal').forEach((modal) => modal.addEventListener('click', (event) => {
    if (event.target === modal) modal.classList.remove('open');
  }));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') $$('.modal.open').forEach((modal) => modal.classList.remove('open'));
  });

  // Principles
  const principleList = $('#principleList');
  if (principleList) {
    principleList.innerHTML = ontology.principles.map((item, index) => `
      <div class="principle"><b>${String(index + 1).padStart(2, '0')}</b><span>${esc(item)}</span></div>
    `).join('');
  }

  // Causal chain
  const chainEl = $('#causalChain');
  const detailTitle = $('#chainDetailTitle');
  const detailEn = $('#chainDetailEn');
  const detailText = $('#chainDetailText');
  function showChain(item, button) {
    $$('.chain-node').forEach((node) => node.classList.remove('active'));
    button?.classList.add('active');
    detailTitle.textContent = item.label;
    detailEn.textContent = item.en;
    detailText.textContent = item.description;
  }
  if (chainEl) {
    ontology.chain.forEach((item, index) => {
      const button = document.createElement('button');
      button.className = `chain-node${index === 0 ? ' active' : ''}`;
      button.type = 'button';
      button.innerHTML = `<span class="num">${String(index + 1).padStart(2, '0')}</span><strong>${esc(item.label)}</strong><small>${esc(item.en)}</small>`;
      button.addEventListener('click', () => showChain(item, button));
      chainEl.appendChild(button);
    });
  }

  // Ontology module explorer
  let selectedModule = ontology.modules[0];
  let selectedTab = 'classes';
  const moduleList = $('#moduleList');
  const moduleTitle = $('#moduleTitle');
  const moduleSubtitle = $('#moduleSubtitle');
  const moduleSummary = $('#moduleSummary');
  const moduleContent = $('#moduleContent');

  function renderModuleList() {
    moduleList.innerHTML = ontology.modules.map((module) => `
      <button class="module-button${module.id === selectedModule.id ? ' active' : ''}" type="button" data-module="${esc(module.id)}">
        <strong>${esc(module.title)}</strong><small>${esc(module.subtitle)}</small>
      </button>
    `).join('');
    $$('.module-button', moduleList).forEach((button) => button.addEventListener('click', () => {
      selectedModule = ontology.modules.find((module) => module.id === button.dataset.module) || ontology.modules[0];
      renderModuleList();
      renderModule();
    }));
  }

  function classContent(module) {
    return `<div class="class-grid">${module.classes.map((cls) => `
      <article class="class-card"><h4>${esc(cls.name)}</h4><p>${esc(cls.definition)}</p><div class="pill-wrap">${cls.children.map((child) => `<span class="pill">${esc(child)}</span>`).join('')}</div></article>
    `).join('')}</div>`;
  }
  function listContent(items, type) {
    const cls = type === 'rules' ? 'rule-row' : type === 'validation' ? 'validation-row' : '';
    return `<div class="list-box">${items.map((item) => `<div class="list-row ${cls}">${type === 'properties' ? `<code>${esc(item)}</code>` : esc(item)}</div>`).join('')}</div>`;
  }
  function renderModule() {
    moduleTitle.textContent = selectedModule.title;
    moduleSubtitle.textContent = selectedModule.subtitle;
    moduleSummary.textContent = selectedModule.summary;
    if (selectedTab === 'classes') moduleContent.innerHTML = classContent(selectedModule);
    else moduleContent.innerHTML = listContent(selectedModule[selectedTab], selectedTab);
  }
  $$('.tab-button').forEach((button) => button.addEventListener('click', () => {
    $$('.tab-button').forEach((tab) => tab.classList.remove('active'));
    button.classList.add('active');
    selectedTab = button.dataset.tab;
    renderModule();
  }));
  renderModuleList();
  renderModule();

  // Evidence roles
  const roleTrack = $('#roleTrack');
  if (roleTrack) {
    roleTrack.innerHTML = ontology.roles.map((role) => `
      <article class="role ${role.code.toLowerCase()}"><div class="role-code">${esc(role.code)}</div><h3>${esc(role.name)}</h3><p>${esc(role.description)}</p><small>${esc(role.animalUse)}</small></article>
    `).join('');
  }

  // Competency questions
  const cq = $('#competencyQuestions');
  if (cq) cq.innerHTML = ontology.competencyQuestions.map((q, i) => `<div class="cq"><strong>${String(i + 1).padStart(2, '0')}.</strong> ${esc(q)}</div>`).join('');

  // GP-L-CT demo
  const inputs = {
    aiDomain: $('#aiDomain'),
    falseNegativeKnown: $('#falseNegativeKnown'),
    namExposure: $('#namExposure'),
    measuredExposure: $('#measuredExposure'),
    kupffer: $('#kupffer'),
    carrierControl: $('#carrierControl'),
    biodistribution: $('#biodistribution'),
    independentStreams: $('#independentStreams'),
    expertReviewed: $('#expertReviewed')
  };
  const roleDefinitions = Object.fromEntries(ontology.roles.map((role) => [role.code, role]));
  const ruleCap = (cap, value) => Math.min(cap, value);

  function getDemoState() {
    return {
      aiDomain: inputs.aiDomain.value,
      falseNegativeKnown: inputs.falseNegativeKnown.checked,
      namExposure: inputs.namExposure.value,
      measuredExposure: inputs.measuredExposure.checked,
      kupffer: inputs.kupffer.checked,
      carrierControl: inputs.carrierControl.checked,
      biodistribution: inputs.biodistribution.value,
      independentStreams: Number(inputs.independentStreams.value),
      expertReviewed: inputs.expertReviewed.checked
    };
  }

  function evaluateDemo(state) {
    let cap = 5;
    let base = 3;
    const gaps = [];
    const recommendations = [];
    const add = (code, text, rec, roleCap = 5) => {
      gaps.push({ code, text });
      if (rec) recommendations.push(rec);
      cap = ruleCap(cap, roleCap);
    };

    if (state.aiDomain === 'out') add('ET‑R001', '저분자 중심 AI 모델이 siRNA 나노의약품에 적용되어 후보가 Out‑of‑domain입니다.', '현재 modality를 포함하는 모델 또는 orthogonal NAM을 사용합니다.', 1);
    else if (state.aiDomain === 'border') add('ET‑R001B', '후보가 applicability domain 경계에 있어 음성예측의 불확실성이 큽니다.', '구조·modality 유사성 분석과 외부검증자료를 보강합니다.', 2);
    else base += 0.4;

    if (!state.falseNegativeKnown) add('ET‑R003', '음성예측의 false‑negative 성능이 확인되지 않았습니다.', '현재 endpoint와 threshold에서 sensitivity와 false‑negative 특성을 확인합니다.', 2);
    else base += 0.35;

    if (state.namExposure === 'single') add('ET‑R007', '계획된 반복투여를 급성 단회 NAM으로만 평가합니다.', '반복노출 NAM 또는 acute‑to‑repeat bridging 근거를 마련합니다.', 2);
    else base += 0.5;

    if (!state.measuredExposure) add('ET‑R006', '명목농도만 존재하고 free 또는 세포내 실제 노출이 확인되지 않았습니다.', 'Free 또는 intracellular exposure를 측정하고 QIVIVE로 연결합니다.', 2);
    else base += 0.55;

    if (!state.kupffer) add('ET‑HR001', 'Kupffer cell 또는 면역 적격 간 모델이 없어 나노입자 관련 면역반응을 평가하기 어렵습니다.', 'Human hepatocyte–Kupffer cell 공배양 또는 cytokine/complement 평가를 추가합니다.', 3);
    else base += 0.45;

    if (!state.carrierControl) add('ET‑R009', 'Carrier‑only 대조군이 없어 전달체의 독성기여도를 분리할 수 없습니다.', 'Carrier‑only와 active‑only 대조군을 포함합니다.', 3);
    else base += 0.35;

    if (state.biodistribution === 'missing') add('ET‑BD001', '간·비장 biodistribution 자료가 없습니다.', '정량적 간·비장 biodistribution과 잔류를 평가합니다.', 2);
    else if (state.biodistribution === 'qualitative') add('ET‑BD002', '정성적 분포만 존재하여 조직노출과 독성을 정량 연결할 수 없습니다.', '정량적 biodistribution과 exposure margin을 확보합니다.', 3);
    else base += 0.55;

    if (state.independentStreams < 2) add('ET‑RWoE', '독립적인 근거 흐름이 1개뿐이어서 Weight of Evidence가 부족합니다.', '기전 또는 사람 관련 독립 근거를 하나 이상 추가합니다.', 2);
    else if (state.independentStreams >= 3) base += 0.45;

    if (!state.expertReviewed) add('ET‑R013', '고영향 결론에 대한 독성전문가 검토가 완료되지 않았습니다.', '독성전문가가 Evidence Role과 동물사용 권고를 승인·수정합니다.', 3);
    else base += 0.45;

    let role = Math.max(1, Math.min(5, Math.floor(base)));
    if (gaps.length >= 6) role = Math.min(role, 2);
    if (gaps.length >= 8) role = 1;
    role = Math.min(role, cap);

    if (role >= 4 && !state.expertReviewed) role = 3;
    if (role === 5 && !(state.aiDomain === 'in' && state.falseNegativeKnown && state.namExposure === 'repeat' && state.measuredExposure && state.kupffer && state.carrierControl && state.biodistribution === 'quantitative' && state.independentStreams >= 3 && state.expertReviewed)) role = 4;

    const code = `R${role}`;
    const roleDef = roleDefinitions[code];
    const animal = role <= 2 ? '동물시험 축소 미지원' : role === 3 ? '시험 정교화 가능 · 축소는 추가검토' : role === 4 ? '제한적 축소 검토 가능' : '특정 endpoint 대체후보';
    return { code, roleDef, animal, gaps, recommendations: [...new Set(recommendations)].slice(0, 6) };
  }

  function renderDemo() {
    const result = evaluateDemo(getDemoState());
    $('#demoRoleCode').textContent = result.code;
    $('#demoRoleName').textContent = result.roleDef.name;
    $('#demoRoleDescription').textContent = result.roleDef.description;
    const status = $('#demoAnimalStatus');
    status.textContent = result.animal;
    status.classList.toggle('ok', Number(result.code.slice(1)) >= 4);
    $('#demoGaps').innerHTML = result.gaps.length ? result.gaps.map((gap) => `<div class="demo-gap"><code>${esc(gap.code)}</code><span>${esc(gap.text)}</span></div>`).join('') : `<div class="demo-gap"><code>NO CRITICAL GAP</code><span>현재 입력에서 핵심 결정 제한요소가 탐지되지 않았습니다. 실제 적용 전 독립적인 전문가 검토가 필요합니다.</span></div>`;
    $('#demoRecommendations').innerHTML = result.recommendations.length ? result.recommendations.map((rec) => `<li>${esc(rec)}</li>`).join('') : '<li>현재 사용범위와 근거 역할을 명확히 문서화하고 전문가 검토를 유지합니다.</li>';
  }

  function setDemoDefaults() {
    const d = gp.defaultInputs;
    inputs.aiDomain.value = d.aiDomain;
    inputs.falseNegativeKnown.checked = d.falseNegativeKnown;
    inputs.namExposure.value = d.namExposure;
    inputs.measuredExposure.checked = d.measuredExposure;
    inputs.kupffer.checked = d.kupffer;
    inputs.carrierControl.checked = d.carrierControl;
    inputs.biodistribution.value = d.biodistribution;
    inputs.independentStreams.value = String(d.independentStreams);
    inputs.expertReviewed.checked = d.expertReviewed;
    renderDemo();
  }
  Object.values(inputs).forEach((input) => input?.addEventListener('change', renderDemo));
  $('#resetDemo')?.addEventListener('click', setDemoDefaults);
  setDemoDefaults();

  // Section observer for subtle navigation state
  const sections = $$('main section[id]');
  const navLinks = $$('#mainNav a');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        navLinks.forEach((link) => link.classList.toggle('active', link.getAttribute('href') === `#${entry.target.id}`));
      });
    }, { rootMargin: '-40% 0px -52% 0px', threshold: 0 });
    sections.forEach((section) => observer.observe(section));
  }
})();
