import sys
import re

with open('scripts/generate_architecture_editor.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix deviationBrief
bad_deviation_brief = """function deviationBrief(){let d=model.deviations||{},n=d.nodes||{},e=d.edges||{};let rows=[];Object.entries(n).forEach(([id,v])=>rows.push(`- Node ${id}: ${v.message}`));Object.entries(e).forEach(([id,v])=>rows.push(`- Edge ${id}: ${v.message}`));if(!rows.length)return '# Development Brief: No Deviations

No deviations available.';return `# Development Brief: Architecture Deviations

## Summary
${d.summary?.message||''}

## Deviations
${rows.join('\\n')}

## Implementation Order
- Fix each deviation exactly at the referenced node/edge.
- Ergänze oder korrigiere fehlende Endpunkte/Verbindungen.
- Führe erneut VALIDATE ARCH aus, bis keine Abweichung mehr rot ist.

## Acceptance Criteria
- [ ] Alle roten Abweichungen sind behoben.
- [ ] Validation meldet "No deviations found".`}"""

good_deviation_brief = """function deviationBrief() {
  const d = model.deviations || {};
  const n = d.nodes || {};
  const e = d.edges || {};
  const rows = [];

  Object.entries(n).forEach(([id, v]) => rows.push(`- Node ${id}: ${v.message}`));
  Object.entries(e).forEach(([id, v]) => rows.push(`- Edge ${id}: ${v.message}`));

  if (!rows.length) {
    return `# Development Brief: No Deviations\\n\\nNo deviations available.`;
  }

  return `# Development Brief: Architecture Deviations\\n\\n## Summary\\n${d.summary?.message || ''}\\n\\n## Deviations\\n${rows.join('\\n')}\\n\\n## Implementation Order\\n- Fix each deviation exactly at the referenced node/edge.\\n- Add or correct missing endpoints/connections.\\n- Run VALIDATE ARCH again until no red deviation remains.\\n\\n## Acceptance Criteria\\n- [ ] All red deviations are fixed.\\n- [ ] Validation reports "No deviations found".`;
}"""
content = content.replace(bad_deviation_brief, good_deviation_brief)

# Fix implicit globals
content = content.replace(
    "let model=JSON.parse(data.textContent),map={},active=null,edit=false,fileName='architecture.md';",
    "const dom = { data: document.getElementById('data'), title: document.getElementById('title'), scene: document.getElementById('scene'), lines: document.getElementById('lines'), panel: document.getElementById('panel'), modal: document.getElementById('modal'), modalTitle: document.getElementById('modalTitle'), modalText: document.getElementById('modalText'), editBtn: document.getElementById('editBtn') };\nlet model=JSON.parse(dom.data.textContent),map={},active=null,edit=false,fileName='architecture.md';"
)

content = content.replace("title.textContent=", "dom.title.textContent=")
content = content.replace("scene.querySelectorAll", "dom.scene.querySelectorAll")
content = content.replace("scene.appendChild", "dom.scene.appendChild")
content = content.replace("lines.innerHTML", "dom.lines.innerHTML")
content = content.replace("lines.appendChild", "dom.lines.appendChild")
content = content.replace("panel.innerHTML", "dom.panel.innerHTML")
content = content.replace("panel.insertAdjacentHTML", "dom.panel.insertAdjacentHTML")
content = content.replace("editBtn.textContent=", "dom.editBtn.textContent=")
content = content.replace("modalTitle.textContent=", "dom.modalTitle.textContent=")
content = content.replace("modalText.value", "dom.modalText.value")
content = content.replace("modal.classList", "dom.modal.classList")

# Fix form fields to not rely on global IDs
content = content.replace("f_label.value", "document.getElementById('f_label').value")
content = content.replace("f_sub.value", "document.getElementById('f_sub').value")
content = content.replace("f_title.value", "document.getElementById('f_title').value")
content = content.replace("f_subtitle.value", "document.getElementById('f_subtitle').value")
content = content.replace("f_notes.value", "document.getElementById('f_notes').value")
content = content.replace("f_tags.value", "document.getElementById('f_tags').value")
content = content.replace("f_flow.value", "document.getElementById('f_flow').value")
content = content.replace("f_method.value", "document.getElementById('f_method').value")
content = content.replace("f_path.value", "document.getElementById('f_path').value")
content = content.replace("f_desc.value", "document.getElementById('f_desc').value")
content = content.replace("f_params.value", "document.getElementById('f_params').value")

with open('scripts/generate_architecture_editor.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied successfully.")
