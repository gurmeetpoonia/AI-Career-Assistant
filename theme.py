import streamlit as st

def inject_3d_theme():
    st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stHeader"] {
        display: none !important;
    }
    .main .block-container {
        padding-left: 5rem !important;
        padding-right: 5rem !important;
    }
    .card-3d {
        padding: 25px; border-radius: 20px; background: #ffffff;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 20px 40px -5px rgba(0, 0, 0, 0.03);
        margin-bottom: 25px; border: 1px solid rgba(0, 0, 0, 0.04);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .card-3d:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 35px -5px rgba(0, 0, 0, 0.1), 0 30px 50px -10px rgba(0, 0, 0, 0.07);
    }
    .result-3d { background: linear-gradient(135deg, #1E40AF, #6D28D9); color: white; }
    .insight-3d { border-top: 5px solid #2563EB; background: linear-gradient(to bottom right, #FFFFFF, #F0F6FF); }
    .recommend-3d { border-top: 5px solid #D97706; background: linear-gradient(to bottom right, #FFFFFF, #FEFBF0); }
    .analysis-3d { border-top: 5px solid #059669; background: linear-gradient(to bottom right, #FFFFFF, #ECFDF5); }
    .feature-card { border-top: 5px solid #EC4899; background: linear-gradient(to bottom right, #FFFFFF, #FDF2F8); } 
    .health-card { border-top: 5px solid #10B981; background: linear-gradient(to bottom right, #FFFFFF, #F0FDF4); }

    .metric-3d {
        background: #ffffff; padding: 20px; border-radius: 16px; text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.04); border: 1px solid #F3F4F6;
    }
    .metric-label { font-size: 0.85rem; color: #6B7280; font-weight: 600; text-transform: uppercase; }
    .metric-val { font-size: 1.8rem; color: #111827; font-weight: 800; margin-top: 5px; }
    .progress-bg { background: #E5E7EB; border-radius: 10px; height: 12px; width: 100%; margin-top: 8px; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: 10px; }
    .badge { padding: 4px 10px; border-radius: 8px; font-weight: bold; font-size: 0.9rem; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)