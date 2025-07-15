# Team Performance Analysis Dashboard

A comprehensive Streamlit application for analyzing and evaluating team performance metrics in processing (CP) and storage (HDD) systems. This dashboard provides automated performance assessment, detailed area analysis, and actionable recommendations.

## 🚀 Features

- **Automated Performance Evaluation**: Real-time analysis of CP and HDD performance metrics
- **Interactive Dashboard**: User-friendly interface with team selection and detailed breakdowns
- **Performance Profiles**: Radar charts showing efficiency, stability, and predictability metrics
- **Area-Specific Analysis**: Detailed breakdown of performance by specific system areas
- **Smart Recommendations**: AI-powered suggestions based on performance scores
- **Ranking System**: Position tracking and category classification
- **Bilingual Support**: Available in English (V1.5.1) and Spanish versions

## 📊 Analysis Capabilities

### Processing (CP) Analysis
- Process load evaluation (PP_NFD)
- I/O operations monitoring (IOLOAD)
- Memory usage analysis (totmem, CUMOVR, OMOVRN, MAXMEM)
- CPU consumption tracking (TLCONS, CPLOAD)
- Load stability assessment (OMLDAV)

### Storage (HDD) Analysis
- Storage efficiency evaluation
- Disk performance stability
- Change rate monitoring
- Unit-specific analysis

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **Data Visualization**: Plotly
- **Data Processing**: Pandas, NumPy
- **Language**: Python 3.8+

## 📁 File Structure

```
├── detalle_equipos_v1.5.1.py    # English version (V1.5.1) - Main app
├── detalle_equipos_v5.py        # Spanish version (V5)
├── ranking_cp.csv              # CP performance data
├── ranking_hdd.csv             # HDD performance data
├── requirements.txt            # Python dependencies
├── .streamlit/config.toml      # Streamlit configuration
└── README.md                   # Documentation
```

## 🚀 Quick Start

### Local Development
1. Clone the repository
   ```bash
   git clone https://github.com/andresriosinfo/dashboard-equipos-cp-hdd-v1.1.git
   cd dashboard-equipos-cp-hdd-v1.1
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application
   ```bash
   streamlit run detalle_equipos_v1.5.1.py
   ```

4. Access the dashboard at `http://localhost:8501`

### Streamlit Cloud Deployment
1. Fork or clone this repository
2. Connect your repository to Streamlit Cloud
3. Deploy using the main file: `detalle_equipos_v1.5.1.py`

## 📈 Performance Metrics

The dashboard evaluates teams based on:
- **Efficiency Score**: Resource utilization optimization
- **Stability Score**: Performance consistency
- **Predictability Score**: Change pattern analysis
- **Overall Score**: Combined performance rating

## 🎯 Use Cases

- IT infrastructure monitoring
- System performance optimization
- Team performance evaluation
- Resource allocation planning
- Performance trend analysis

## 🔧 Configuration

The application automatically loads performance data from CSV files and provides real-time analysis without additional configuration required.

### Data Requirements
- `ranking_cp.csv`: Contains CP performance metrics and scores
- `ranking_hdd.csv`: Contains HDD performance metrics and scores

### Streamlit Configuration
The app uses a custom theme defined in `.streamlit/config.toml` for optimal user experience.

## 📊 Dashboard Sections

1. **General Information**: Team overview and basic metrics
2. **Ranking Position**: Current position in performance rankings
3. **System Recommendations**: AI-generated improvement suggestions
4. **Performance Profiles**: Visual radar charts for CP and HDD metrics
5. **Area Analysis**: Detailed breakdown by specific performance areas

## 🚨 Performance Categories

- **🟢 Excellent (80-100)**: Optimal performance, maintain current practices
- **🟡 Good (60-79)**: Good performance with room for improvement
- **🟠 Regular (40-59)**: Requires optimization and monitoring
- **🔴 Low (0-39)**: Immediate attention and improvements needed

## 🔄 Version History

- **V1.5.1**: English version with enhanced UI and comprehensive analysis
- **V5**: Spanish version with full functionality
- **V6**: Dashboard-style layout with improved user experience

## 📝 License

Developed by InfoDesign Colombia | 2024

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

**Live Demo**: [Streamlit Cloud URL will be available after deployment] 