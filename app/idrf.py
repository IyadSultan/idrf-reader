"""The 20 image-defined risk factors (INRG staging system; Monclair et al., JCO 2009;
definitions per Brisse et al., Radiology 2011). Single source of truth for the API and UI."""

GROUPS = [
    {"id": "comp", "name": "Multiple compartments", "items": [
        {"id": "comp2", "t": "Ipsilateral tumour extension within two body compartments: neck–chest, chest–abdomen, or abdomen–pelvis", "s": "Two compartments"}]},
    {"id": "neck", "name": "Neck", "items": [
        {"id": "neck_vessels", "t": "Tumour encases the carotid and/or vertebral artery and/or the internal jugular vein", "s": "Neck vessels"},
        {"id": "neck_skull", "t": "Tumour extends to the base of the skull", "s": "Skull base"},
        {"id": "neck_trachea", "t": "Tumour compresses the trachea", "s": "Trachea, neck"}]},
    {"id": "cerv", "name": "Cervico-thoracic junction", "items": [
        {"id": "ct_plexus", "t": "Tumour encases the brachial plexus roots", "s": "Brachial plexus"},
        {"id": "ct_vessels", "t": "Tumour encases the subclavian vessels and/or the vertebral and/or carotid artery", "s": "Subclavian vessels"},
        {"id": "ct_trachea", "t": "Tumour compresses the trachea", "s": "Trachea, junction"}]},
    {"id": "thor", "name": "Thorax", "items": [
        {"id": "th_aorta", "t": "Tumour encases the aorta and/or its major branches", "s": "Thoracic aorta"},
        {"id": "th_airway", "t": "Tumour compresses the trachea and/or the principal bronchi", "s": "Airway"},
        {"id": "th_costo", "t": "Lower mediastinal tumour infiltrating the costo-vertebral junction between T9 and T12", "s": "Costo-vertebral junction",
         "h": "Risk of injury to the artery of Adamkiewicz, which usually arises at this level."}]},
    {"id": "thab", "name": "Thoraco-abdominal", "items": [
        {"id": "ta_vessels", "t": "Tumour encases the aorta and/or the vena cava", "s": "Aorta or IVC, thoraco-abdominal"}]},
    {"id": "abd", "name": "Abdomen and pelvis", "items": [
        {"id": "ab_porta", "t": "Tumour infiltrates the porta hepatis and/or the hepatoduodenal ligament", "s": "Porta hepatis"},
        {"id": "ab_smab", "t": "Tumour encases branches of the superior mesenteric artery (SMA) at the mesenteric root", "s": "SMA branches"},
        {"id": "ab_origin", "t": "Tumour encases the origin of the coeliac axis and/or the origin of the SMA", "s": "Coeliac or SMA origin"},
        {"id": "ab_renal", "t": "Tumour invades one or both renal pedicles", "s": "Renal pedicle"},
        {"id": "ab_aorta", "t": "Tumour encases the aorta and/or the vena cava", "s": "Aorta or IVC"},
        {"id": "ab_iliac", "t": "Tumour encases the iliac vessels", "s": "Iliac vessels"},
        {"id": "ab_sciatic", "t": "Pelvic tumour crosses the sciatic notch", "s": "Sciatic notch"}]},
    {"id": "spine", "name": "Spinal canal (any level)", "items": [
        {"id": "spine", "t": "Intraspinal tumour extension (at any level) with ANY of: (a) more than one third of the spinal canal invaded on axial images; (b) perimedullary leptomeningeal spaces not visible; (c) abnormal spinal cord signal", "s": "Intraspinal extension"}]},
    {"id": "organs", "name": "Adjacent organs", "items": [
        {"id": "organs", "t": "Tumour infiltrates adjacent organs or structures: pericardium, diaphragm, kidney, liver, duodeno-pancreatic block, mesentery", "s": "Adjacent organs"}]},
]

ITEMS = [dict(it, g=g["id"]) for g in GROUPS for it in g["items"]]
ITEM_IDS = [i["id"] for i in ITEMS]
SHORT = {i["id"]: i["s"] for i in ITEMS}
VALID = {"absent", "present", "na"}

assert len(ITEM_IDS) == 20 and len(set(ITEM_IDS)) == 20
