import matplotlib
matplotlib.use('Agg')  # GUI 백엔드 대신 Agg 백엔드를 사용
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from io import BytesIO
import base64

def get_stock_code(stock_name):
    """주식 이름으로 종목 코드를 찾는 함수"""
    stock_codes = {
        '삼성전자': '005930',
        'SK하이닉스': '000660',
        'NAVER': '035420',
        '카카오': '035720'
    }
    return stock_codes.get(stock_name)

def get_stock_data(code, period='1y'):
    """주식 데이터를 가져오는 함수"""
    try:
        ticker = f"{code}.KS"
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return None
        
        return df
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return {"error": f"Failed to fetch stock data: {str(e)}"}

def cal_increase(code, interval='monthly'):
    """주가 상승률을 계산하는 함수"""
    try:
        df = get_stock_data(code)
        
        if df is None or df.empty:
            return None
            
        if interval == 'monthly':
            df_resampled = df.resample('ME').last()  # 'M'을 'ME'로 변경
        else:  # weekly
            df_resampled = df.resample('W').last()
            
        df_resampled['Increase'] = df_resampled['Close'].diff()
        df_resampled['Increase_Rate'] = df_resampled['Close'].pct_change() * 100
        
        return df_resampled
    except Exception as e:
        print(f"Error calculating increase: {e}")
        return None

def cal_data(code):
    """주식 분석 데이터를 계산하는 함수"""
    try:
        df = get_stock_data(code)
        
        if df is None or df.empty:
            return {"error": "Failed to fetch stock data"}
            
        df_monthly = cal_increase(code, interval='monthly')
        df_weekly = cal_increase(code, interval='weekly')
        
        if df_monthly is None or df_weekly is None or df_monthly.empty or df_weekly.empty:
            return {"error": "Failed to calculate data"}
        
        # 통계 데이터 계산
        stats = {
            "monthly": {
                "increase": float(df_monthly['Increase'].iloc[-1]),
                "increase_rate": float(df_monthly['Increase_Rate'].iloc[-1]),
                "mean": float(df_monthly['Increase'].mean()),
                "std": float(df_monthly['Increase'].std()),
                "max": float(df_monthly['Increase'].max()),
                "min": float(df_monthly['Increase'].min())
            },
            "weekly": {
                "increase": float(df_weekly['Increase'].iloc[-1]),
                "increase_rate": float(df_weekly['Increase_Rate'].iloc[-1]),
                "mean": float(df_weekly['Increase'].mean()),
                "std": float(df_weekly['Increase'].std()),
                "max": float(df_weekly['Increase'].max()),
                "min": float(df_weekly['Increase'].min())
            },
            "current_price": float(df['Close'].iloc[-1])
        }
        
        # 시각화 데이터 생성
        visualization = create_visualization(df_monthly, df_weekly)
        
        return {
            "statistics": stats,
            "visualization": visualization
        }
    except Exception as e:
        print(f"Error in cal_data: {e}")
        return {"error": f"Analysis failed: {str(e)}"}

def create_visualization(df_monthly, df_weekly):
    """시각화 데이터 생성 함수"""
    try:
        # 그래프 생성
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # 월별 증가율 그래프
        ax1.plot(df_monthly.index, df_monthly['Increase_Rate'], 'b-', label='Monthly')
        ax1.set_title('Monthly Increase Rate')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Increase Rate (%)')
        ax1.grid(True)
        ax1.legend()
        
        # 주별 증가율 그래프
        ax2.plot(df_weekly.index, df_weekly['Increase_Rate'], 'r-', label='Weekly')
        ax2.set_title('Weekly Increase Rate')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Increase Rate (%)')
        ax2.grid(True)
        ax2.legend()
        
        plt.tight_layout()
        
        # 그래프를 이미지로 변환
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        # 이미지를 base64로 인코딩
        graph = base64.b64encode(image_png).decode('utf-8')
        
        return {
            "graph": graph,
            "monthly_data": {
                "dates": df_monthly.index.strftime('%Y-%m-%d').tolist(),
                "values": df_monthly['Increase_Rate'].tolist()
            },
            "weekly_data": {
                "dates": df_weekly.index.strftime('%Y-%m-%d').tolist(),
                "values": df_weekly['Increase_Rate'].tolist()
            }
        }
    except Exception as e:
        print(f"Error in visualization: {e}")
        return None

def predict_increase(code):
    """주가 상승 예측 함수"""
    try:
        df = get_stock_data(code)
        if df is None or df.empty:
            return {"error": "Failed to fetch stock data"}
            
        last_price = float(df['Close'].iloc[-1])
        avg_price = float(df['Close'].mean())
        
        # 추가적인 예측 지표 계산
        moving_avg_20 = df['Close'].rolling(window=20).mean().iloc[-1]
        moving_avg_60 = df['Close'].rolling(window=60).mean().iloc[-1]
        
        # 예측 신뢰도 계산 (예시)
        confidence = 0.6
        if moving_avg_20 > moving_avg_60:
            confidence += 0.2
        if last_price > moving_avg_20:
            confidence += 0.2
            
        return {
            "prediction": last_price > avg_price,
            "confidence": confidence,
            "indicators": {
                "last_price": last_price,
                "average_price": avg_price,
                "moving_avg_20": float(moving_avg_20),
                "moving_avg_60": float(moving_avg_60)
            }
        }
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}