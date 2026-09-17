export type Language = 'en' | 'ta' | 'hi';

export interface TranslationDictionary {
  brandTitle: string;
  tagline: string;
  coreThesis: string;
  coreThesisSecondary: string;
  viewLabel: string;
  trustGateVisual: string;
  plantIntake: string;
  blueprint: string;
  provenance: string;
  benchmark: string;
  chemistryDemo: string;
  scenarioNormal: string;
  scenarioStress: string;
  reliabilityGatePass: string;
  reliabilityGateAbstain: string;
  decisionOperate: string;
  decisionCleaningReview: string;
  decisionAbstain: string;
  fallbackActive: string;
  aiActionWithheld: string;
}

export const TRANSLATIONS: Record<Language, TranslationDictionary> = {
  en: {
    brandTitle: 'PLANT-X / FOUL-X',
    tagline: 'Trust-Gated Industrial Process Intelligence',
    coreThesis: '"FOUL-X does not treat every prediction as actionable."',
    coreThesisSecondary: 'It separates prognosis from decision by evaluating whether evidence supports the prediction.',
    viewLabel: 'VIEW:',
    trustGateVisual: 'TRUST GATE VISUAL',
    plantIntake: 'PLANT INTAKE',
    blueprint: 'BLUEPRINT',
    provenance: 'PROVENANCE',
    benchmark: 'BENCHMARK',
    chemistryDemo: 'CHEMISTRY DEMO',
    scenarioNormal: 'NORMAL REGIME',
    scenarioStress: '+6σ STRESS SHIFT',
    reliabilityGatePass: 'GATE: PASS',
    reliabilityGateAbstain: 'GATE: ABSTAIN',
    decisionOperate: 'OPERATE (NOMINAL)',
    decisionCleaningReview: 'CLEANING WINDOW — REVIEW',
    decisionAbstain: 'AI ACTION WITHHELD — FIXED POLICY ACTIVE',
    fallbackActive: 'Fixed cleaning policy active (90-day interval)',
    aiActionWithheld: 'AI recommendation withheld due to out-of-support operating regime',
  },
  ta: {
    brandTitle: 'பிளாண்ட்-எக்ஸ் / ஃபவுல்-எக்ஸ்',
    tagline: 'நம்பகத்தன்மை சரிபார்க்கப்பட்ட தொழிற்துறை செயல்முறை அறிவு',
    coreThesis: '"ஃபவுல்-எக்ஸ் அனைத்து கணிப்புகளையும் செயல்பாட்டிற்குரியதாக கருதுவதில்லை."',
    coreThesisSecondary: 'ஆதாரம் கணிப்பை ஆதரிக்கிறதா என்பதை மதிப்பிடுவதன் மூலம் இது கணிப்பை முடிவிலிருந்து பிரிக்கிறது.',
    viewLabel: 'பார்வை:',
    trustGateVisual: 'நம்பக வாயில் வரைபடம்',
    plantIntake: 'ஆலை தரவு உட்செலுத்தல்',
    blueprint: 'செயல்முறை வரைபடம்',
    provenance: 'மாதிரி தோற்றம்',
    benchmark: 'செயல்திறன் அளவுகோல்',
    chemistryDemo: 'வேதியியல் மாதிரி',
    scenarioNormal: 'இயல்பு நிலை',
    scenarioStress: '+6σ அழுத்த மாற்றம்',
    reliabilityGatePass: 'வாயில்: தேர்ச்சி',
    reliabilityGateAbstain: 'வாயில்: விலகல் (ABSTAIN)',
    decisionOperate: 'இயக்கு (இயல்பு)',
    decisionCleaningReview: 'தூய்மையாக்கல் ஆய்வு தேவை',
    decisionAbstain: 'செயற்கை நுண்ணறிவு பரிந்துரை நிறுத்திவைக்கப்பட்டது',
    fallbackActive: 'நிலையான பராமரிப்பு கொள்கை செயல்பாட்டில் உள்ளது',
    aiActionWithheld: 'வரம்பிற்கு வெளியே உள்ள இயக்க நிலை காரணமாக பரிந்துரை நிறுத்தப்பட்டது',
  },
  hi: {
    brandTitle: 'प्लांट-एक्स / फाउल-एक्स',
    tagline: 'विश्वसनीयता-सत्यापित औद्योगिक प्रक्रिया इंटेलिजेंस',
    coreThesis: '"फाउल-एक्स हर भविष्यवाणी को कार्रवाई योग्य नहीं मानता।"',
    coreThesisSecondary: 'यह मूल्यांकन करके कि साक्ष्य भविष्यवाणी का समर्थन करते हैं या नहीं, पूर्वानुमान को निर्णय से अलग करता है।',
    viewLabel: 'दृश्य:',
    trustGateVisual: 'विश्वसनीयता गेट दृश्य',
    plantIntake: 'प्लांट डेटा इनटेक',
    blueprint: 'ब्लूप्रिंट (पीएंडआईडी)',
    provenance: 'मॉडल उत्पत्ति',
    benchmark: 'मानदंड (बेंचमार्क)',
    chemistryDemo: 'रसायन विज्ञान सिमुलेशन',
    scenarioNormal: 'सामान्य शासन',
    scenarioStress: '+6σ तनाव बदलाव',
    reliabilityGatePass: 'गेट: पास',
    reliabilityGateAbstain: 'गेट: परहेज़ (ABSTAIN)',
    decisionOperate: 'संचालन (सामान्य)',
    decisionCleaningReview: 'सफाई समीक्षा अनुशंसित',
    decisionAbstain: 'एआई कार्रवाई रोक दी गई — निश्चित नीति सक्रिय',
    fallbackActive: 'फिक्स्ड रखरखाव नीति सक्रिय है',
    aiActionWithheld: 'समर्थन से बाहर ऑपरेटिंग शासन के कारण एआई सिफारिश रोक दी गई',
  },
};
