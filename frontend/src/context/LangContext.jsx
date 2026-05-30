import { createContext, useContext, useState } from 'react'

const LangContext = createContext(null)

export const LANGS = {
  en: { label: 'EN', full: 'English' },
  hi: { label: 'हि', full: 'हिंदी' },
  gu: { label: 'ગુ', full: 'ગુજરાતી' },
}

export const T = {
  en: {
    upload: 'Upload Report', history: 'History', compare: 'Compare',
    analyseBtn: 'Analyse Report', analysing: 'Analysing your report...',
    patientName: 'Patient Name', optional: 'optional',
    dropText: 'Drop your PDF here or click to browse',
    dropHint: 'Supports digital and scanned PDF reports',
    heroTitle1: 'Understand Your', heroTitle2: 'Lab Report',
    heroSub: 'Upload any medical report and get a clear, plain-English explanation in seconds.',
    disclaimer: 'This tool explains reports in simple terms only. It does not provide a medical diagnosis. Always consult your doctor.',
    totalTests: 'Total Tests', normal: 'Normal', needAttention: 'Need Attention', critical: 'Critical',
    overallSummary: 'Overall Summary', valuesAttention: 'Values Needing Attention',
    normalValues: 'Normal Values', askDoctor: 'Questions to Ask Your Doctor',
    askDoctorSub: 'Based on your results — bring these up at your next appointment',
    exportPDF: 'Export PDF', compareReports: 'Compare Reports',
    refRange: 'Reference Range', backToUpload: 'Analyse Another Report',
    loginTitle: 'Welcome back', registerTitle: 'Create account',
    email: 'Email', password: 'Password', name: 'Full Name',
    loginBtn: 'Sign In', registerBtn: 'Create Account',
    noAccount: "Don't have an account?", hasAccount: 'Already have an account?',
    signUp: 'Sign up', signIn: 'Sign in', logout: 'Logout',
    selectReport: 'Select Report', selectTwo: 'Select two reports to compare',
    compareBtn: 'Compare Reports', improved: 'Improved', worsened: 'Worsened',
    stable: 'Stable', new: 'New', noHistory: 'No reports yet',
    noHistorySub: 'Upload a lab report to see it here.',
    backendDown: 'Cannot connect to server. Make sure the Flask backend is running on port 5000.',
    networkError: 'Network error — check your internet connection.',
    howWorks: 'How it works',
  },
  hi: {
    upload: 'रिपोर्ट अपलोड करें', history: 'इतिहास', compare: 'तुलना करें',
    analyseBtn: 'रिपोर्ट विश्लेषण करें', analysing: 'आपकी रिपोर्ट का विश्लेषण हो रहा है...',
    patientName: 'मरीज का नाम', optional: 'वैकल्पिक',
    dropText: 'अपना PDF यहाँ छोड़ें या ब्राउज़ करें',
    dropHint: 'डिजिटल और स्कैन की गई PDF रिपोर्ट समर्थित हैं',
    heroTitle1: 'अपनी', heroTitle2: 'लैब रिपोर्ट समझें',
    heroSub: 'कोई भी मेडिकल रिपोर्ट अपलोड करें और सेकंडों में सरल हिंदी में स्पष्टीकरण पाएं।',
    disclaimer: 'यह टूल केवल सरल भाषा में रिपोर्ट समझाता है। यह चिकित्सा निदान नहीं है। हमेशा अपने डॉक्टर से परामर्श करें।',
    totalTests: 'कुल परीक्षण', normal: 'सामान्य', needAttention: 'ध्यान चाहिए', critical: 'गंभीर',
    overallSummary: 'समग्र सारांश', valuesAttention: 'ध्यान देने योग्य मूल्य',
    normalValues: 'सामान्य मूल्य', askDoctor: 'डॉक्टर से पूछने के प्रश्न',
    askDoctorSub: 'आपके परिणामों के आधार पर — अगली मुलाकात में ये पूछें',
    exportPDF: 'PDF निर्यात करें', compareReports: 'रिपोर्ट तुलना करें',
    refRange: 'संदर्भ सीमा', backToUpload: 'दूसरी रिपोर्ट विश्लेषण करें',
    loginTitle: 'वापस स्वागत है', registerTitle: 'खाता बनाएं',
    email: 'ईमेल', password: 'पासवर्ड', name: 'पूरा नाम',
    loginBtn: 'साइन इन करें', registerBtn: 'खाता बनाएं',
    noAccount: 'खाता नहीं है?', hasAccount: 'पहले से खाता है?',
    signUp: 'साइन अप', signIn: 'साइन इन', logout: 'लॉगआउट',
    selectReport: 'रिपोर्ट चुनें', selectTwo: 'तुलना के लिए दो रिपोर्ट चुनें',
    compareBtn: 'तुलना करें', improved: 'सुधरा', worsened: 'बिगड़ा',
    stable: 'स्थिर', new: 'नया', noHistory: 'अभी कोई रिपोर्ट नहीं',
    noHistorySub: 'लैब रिपोर्ट अपलोड करें।',
    backendDown: 'सर्वर से कनेक्ट नहीं हो सका। Flask बैकएंड चल रहा है या नहीं जांचें।',
    networkError: 'नेटवर्क त्रुटि — इंटरनेट कनेक्शन जांचें।',
    howWorks: 'यह कैसे काम करता है',
  },
  gu: {
    upload: 'રિપોર્ટ અપલોડ કરો', history: 'ઇતિહાસ', compare: 'સરખામણી',
    analyseBtn: 'રિપોર્ટ વિશ્લેષણ કરો', analysing: 'તમારી રિપોર્ટ વિશ્લેષણ થઈ રહ્યું છે...',
    patientName: 'દર્દીનું નામ', optional: 'વૈકલ્પિક',
    dropText: 'તમારી PDF અહીં છોડો અથવા બ્રાઉઝ કરો',
    dropHint: 'ડિજિટલ અને સ્કેન કરેલ PDF રિપોર્ટ સપોર્ટ છે',
    heroTitle1: 'તમારો', heroTitle2: 'લેબ રિપોર્ટ સમજો',
    heroSub: 'કોઈ પણ મેડિકલ રિપોર્ટ અપલોડ કરો અને સેકન્ડોમાં સ્પષ્ટ ગુજરાતીમાં સ્પષ્ટીકરણ મેળવો.',
    disclaimer: 'આ ટૂલ ફક્ત સરળ ભાષામાં રિપોર્ટ સમજાવે છે. આ તબીબી નિદાન નથી. હંમેશા ડૉક્ટરની સલાહ લો.',
    totalTests: 'કુલ પરીક્ષણ', normal: 'સામાન્ય', needAttention: 'ધ્યાન જોઈએ', critical: 'ગંભીર',
    overallSummary: 'સમગ્ર સારાંશ', valuesAttention: 'ધ્યાન આપવા યોગ્ય મૂલ્યો',
    normalValues: 'સામાન્ય મૂલ્યો', askDoctor: 'ડૉક્ટરને પૂછવાના પ્રશ્નો',
    askDoctorSub: 'તમારા પરિણામો આધારે — આગળની મુલાકાતમાં આ પૂછો',
    exportPDF: 'PDF નિકાસ કરો', compareReports: 'રિપોર્ટ સરખાવો',
    refRange: 'સંદર્ભ સ્તર', backToUpload: 'બીજી રિપોર્ટ વિશ્લેષણ કરો',
    loginTitle: 'પાછા સ્વાગત છે', registerTitle: 'ખાતું બનાવો',
    email: 'ઈમેઈલ', password: 'પાસવર્ડ', name: 'પૂરું નામ',
    loginBtn: 'સાઇન ઇન', registerBtn: 'ખાતું બનાવો',
    noAccount: 'ખાતું નથી?', hasAccount: 'પહેલેથી ખાતું છે?',
    signUp: 'સાઇન અપ', signIn: 'સાઇન ઇન', logout: 'લૉગઆઉટ',
    selectReport: 'રિપોર્ટ પસંદ કરો', selectTwo: 'સરખામણી માટે બે રિપોર્ટ પસંદ કરો',
    compareBtn: 'સરખાવો', improved: 'સુધર્યું', worsened: 'બગડ્યું',
    stable: 'સ્થિર', new: 'નવું', noHistory: 'હજી કોઈ રિપોર્ટ નથી',
    noHistorySub: 'લેબ રિપોર્ટ અપલોડ કરો.',
    backendDown: 'સર્વર સાથે કનેક્ટ થઈ શક્યું નહીં. Flask બેકએન્ડ ચાલી રહ્યું છે કે નહીં તપાસો.',
    networkError: 'નેટવર્ક ભૂલ — ઇન્ટરનેટ કનેક્શન તપાસો.',
    howWorks: 'આ કેવી રીતે કામ કરે છે',
  }
}

export function LangProvider({ children }) {
  const [lang, setLang] = useState(() => localStorage.getItem('medeasy_lang') || 'en')
  const switchLang = (l) => { setLang(l); localStorage.setItem('medeasy_lang', l) }
  const t = T[lang] || T.en
  return (
    <LangContext.Provider value={{ lang, switchLang, t }}>
      {children}
    </LangContext.Provider>
  )
}

export const useLang = () => useContext(LangContext)
