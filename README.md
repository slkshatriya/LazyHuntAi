# 💫 LazyHuntAi: Your Resume Assistant

LazyHuntAi is a **Streamlit-based web app** that helps job seekers create and update resumes with ease.  
It can generate a professional resume from scratch OR update the skills in an existing resume automatically based on a job description.

---

## ✨ Features
- 📄 **Build Resume from Scratch**  
  Enter your details (name, summary, experience, education, skills) and generate a polished PDF instantly.

- 🔁 **Update Skills in Existing Resume**  
  Upload your `.docx` resume and provide a job post URL → the app extracts relevant skills and updates your resume automatically.

- 🧠 **Powered by NLP**  
  Uses `spaCy` with `en_core_web_sm` model to detect and extract skills from job descriptions.

- ⚡ **Tech Stack**  
  - [Python](https://www.python.org/)  
  - [Streamlit](https://streamlit.io/)  
  - [spaCy](https://spacy.io/)  
  - [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/)  
  - [ReportLab](https://www.reportlab.com/)  
  - [python-docx](https://python-docx.readthedocs.io/)

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/slkshatriya/lazyhuntai.git
cd lazyhuntai
pip install -r requirements.txt
streamlit run app.py

---

📂 Project Structure

lazyhuntai/
├── app.py               # Streamlit app
├── requirements.txt     # Dependencies
└── README.md            # Documentation

🤝 Contributing

Contributions are welcome! 🎉

If you'd like to add new features, improve the UI, or fix bugs:

Fork the repo

Create a new branch (git checkout -b feature-xyz)

Commit your changes (git commit -m "Added new feature")

Push to your branch (git push origin feature-xyz)

Open a Pull Request

📜 License

This project is open-source under the MIT License.

