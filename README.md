# 🌿 GramSwasth: Revolutionizing Rural Healthcare

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-green)
![React](https://img.shields.io/badge/React-18.x-blue)

## 🔍 What is GramSwasth?

GramSwasth is an AI-powered healthcare platform designed to bridge the gap between rural communities and quality medical support. With multilingual capabilities, easy access to healthcare professionals, and AI-driven insights, GramSwasth ensures everyone, regardless of language or location, can access essential healthcare services.

## ✨ Features We Are Building

We are integrating cutting-edge AI and location-based services to make healthcare more accessible:

### 🤖 Multilingual AI Health Assistant (Swasth Mitra AI)
- Users can input health conditions, symptoms, or queries in any Indian native language (text or audio) and receive responses in the same language
- Powered by AI-driven insights, providing accurate remedies, treatments, and guidance
- Built with aiXplain custom agents, ensuring high accuracy and adaptability for rural healthcare needs

### 👨‍⚕️ Doctor Discovery & Appointment Booking (Swasth Connect)
- Helps users find relevant doctors based on symptoms and health conditions
- Provides a curated list of doctors with details like hospital affiliations, fees, experience, and specialization
- Connects rural users with urban specialists

### 🗺️ Locate Nearest Healthcare Facilities (Swasth Map)
- Uses Google Maps to find nearby hospitals, clinics, and health centers
- Powerful tool to locate the nearest healthcare facilities based on user location and medical needs
- Helps users save time during emergencies

### 📰 Health Education & Awareness (Swasth Pulse)
- Keeps users informed about health-related news, conditions, and updates specific to their area
- Offers expert-curated blogs, articles, and news to promote health literacy and preventive care

### 📊 Health Insights Dashboard (Swasth View)
- Interactive visualizations showing urban-rural health disparities in India
- Charts and graphs for different health metrics including:
  - Urban vs rural healthcare access comparison
  - Common health conditions prevalence
  - Life expectancy trends over time
  - Child mortality rates and improvements
- Provides key takeaways and insights to drive informed healthcare decisions
- Responsive design that works across all device sizes

## 🚀 Future Updates

### 📊 AI-powered Demand Forecasting of Medicines
- Predicts the demand for medicines in specific areas, ensuring better supply chain management
- Helps pharmacies stock essential drugs based on demand trends

### 🔮 Disease Outbreak Prediction
- Uses historical data to predict potential disease outbreaks in particular regions
- Helps authorities take preventive action before diseases spread

## 💻 Technology Stack

GramSwasth is built using modern, scalable technologies:

- **Frontend**: React, Next.js, TypeScript, Framer, Vercel
- **Backend**: Flask, JavaScript, Python
- **AI/ML**: aiXplain custom agents, Google Maps integration

## 🛠️ Setup and Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/gram-aarogya.git
cd gram-aarogya
```

2. Set up environment variables in a `.env` file:
```
TEAM_API_KEY=your_team_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
DOC_MODEL_ID=your_doc_model_id
SUMM_MODEL_ID=your_summ_model_id
NEWS_MODEL_ID=your_news_model_id
AGENT_MODEL_ID=your_agent_model_id
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
python backend.py
```

## 🌐 API Endpoints

### Health Assistant
```
POST /ask
```
Body:
```json
{
  "question": "What are the symptoms of dengue?"
}
```

### Doctor Discovery
```
POST /doctors
```
Body:
```json
{
  "condition": "diabetes",
  "location": "Mumbai"
}
```

### Health Centers
```
POST /health-centers
```
Body:
```json
{
  "latitude": 19.0760,
  "longitude": 72.8777
}
```

### Health News
```
POST /news
```
Body:
```json
{
  "language": "hindi"
}
```

## ⚠️ Challenges & Known Issues

- **Internet Connectivity**: Rural areas may face challenges with consistent internet access
- **Digital Literacy**: Some users may require training to navigate the app effectively
- **Data Privacy**: Ensuring user data security and compliance with healthcare regulations
- **Language Accuracy**: Achieving 100% accuracy in translations for all dialects is an ongoing challenge
- **Real-Time Updates**: Keeping healthcare facility information up-to-date in real-time

## 🙏 Acknowledgments

- aiXplain for AI model support & custom model creation
- Google Maps API for location services

---

> **Because everyone deserves good health—anytime, anywhere.**

## 👤 Author

For any questions or issues, please open an issue on GitHub: [@Siddharth Mishra](https://github.com/Sid3503)

---

<p align="center">
  Made with ❤️ and lots of ☕
</p>
# SwasthAI
