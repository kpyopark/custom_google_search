import streamlit as st
import requests
import json
from PIL import Image
import io
from dotenv import load_dotenv
import os
from google_images_search import GoogleImagesSearch


load_dotenv()


# Google Custom Search API 설정
def configure_google_api():
    # 실제 사용시에는 이 값들을 환경변수나 st.secrets에서 가져와야 합니다
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_CX = os.getenv("GOOGLE_CX")
    return GoogleImagesSearch(GOOGLE_API_KEY, GOOGLE_CX)

def search_images(gis, query, num_results=5):
    search_params = {
        'q': query,
        'num': num_results,
        'safe': 'high',
        'fileType': 'jpg|png',
        'rights': 'cc_publicdomain|cc_attribute|cc_sharealike'
    }
    
    try:
        gis.search(search_params)
        return [(item.url, item.title) for item in gis.results()]
    except Exception as e:
        st.error(f"이미지 검색 중 오류 발생: {str(e)}")
        return []

def main():
    st.title("이미지 검색 및 분석 앱")
    
    # 레이아웃 설정
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("이미지 검색")
        search_query = st.text_input("검색어를 입력하세요")
        num_results = st.slider("검색 결과 수", 1, 10, 5)
        
        if st.button("검색"):
            if search_query:
                gis = configure_google_api()
                results = search_images(gis, search_query, num_results)
                
                if results:
                    st.session_state['search_results'] = results
                    st.session_state['selected_image'] = None
                    
                    for i, (url, title) in enumerate(results):
                        try:
                            response = requests.get(url)
                            image = Image.open(io.BytesIO(response.content))
                            st.image(image, caption=title, use_column_width=True)
                            if st.button(f"이미지 {i+1} 선택"):
                                st.session_state['selected_image'] = (url, title)
                        except Exception as e:
                            st.error(f"이미지 로드 중 오류 발생: {str(e)}")
    
    with col2:
        st.header("이미지 분석")
        if 'selected_image' in st.session_state and st.session_state['selected_image']:
            url, title = st.session_state['selected_image']
            try:
                response = requests.get(url)
                image = Image.open(io.BytesIO(response.content))
                st.image(image, caption=title, use_column_width=True)
                
                # 이미지 분석 옵션
                analysis_type = st.selectbox(
                    "분석 유형 선택",
                    ["객체 감지", "텍스트 추출", "얼굴 감지", "라벨 감지"]
                )
                
                if st.button("분석 시작"):
                    # 여기에 선택된 분석 유형에 따른 추가 분석 로직 구현
                    st.info(f"{analysis_type} 분석 결과가 여기에 표시됩니다.")
                    
            except Exception as e:
                st.error(f"이미지 로드 중 오류 발생: {str(e)}")
        else:
            st.info("왼쪽에서 이미지를 선택해주세요.")

if __name__ == "__main__":
    main()