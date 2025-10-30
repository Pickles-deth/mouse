import streamlit as st
import os
from PIL import Image
from datetime import datetime
import zipfile
import io

# ベースフォルダ
BASE_DIR = "mice_data"
os.makedirs(BASE_DIR, exist_ok=True)

st.set_page_config(page_title="マウス耳写真管理", layout="wide")

st.title("🐭 マウス耳写真管理アプリ")

# --- マウス登録・削除 ---
st.subheader("🧬 マウス登録")

mouse_list_file = os.path.join(BASE_DIR, "mice_list.txt")

# マウスリストの読み込み
if os.path.exists(mouse_list_file):
    with open(mouse_list_file, "r") as f:
        mice = [line.strip() for line in f.readlines()]
else:
    mice = []

col1, col2 = st.columns([2, 1])

with col1:
    new_mouse = st.text_input("新しいマウス番号を入力", placeholder="例: 001")
    if st.button("登録"):
        if new_mouse and new_mouse not in mice:
            mice.append(new_mouse)
            with open(mouse_list_file, "a") as f:
                f.write(new_mouse + "\n")
            st.success(f"マウス {new_mouse} を登録しました")
        else:
            st.warning("すでに存在するか、入力が空です。")

with col2:
    delete_mouse = st.selectbox("削除するマウスを選択", [""] + mice)
    if st.button("削除"):
        if delete_mouse:
            mice.remove(delete_mouse)
            with open(mouse_list_file, "w") as f:
                f.writelines([m + "\n" for m in mice])
            st.warning(f"マウス {delete_mouse} を削除しました")

st.divider()

# --- マウス写真アップロード ---
st.subheader("📸 写真アップロード")

if mice:
    selected_mouse = st.selectbox("マウス番号を選択", mice)

    # 今日の日付フォルダ
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_dir = os.path.join(BASE_DIR, today_str)
    os.makedirs(today_dir, exist_ok=True)

    # マウス個別フォルダ
    mouse_folder = os.path.join(today_dir, selected_mouse)
    os.makedirs(mouse_folder, exist_ok=True)

    left_col, right_col = st.columns(2)

    for side, col in zip(["左", "右"], [left_col, right_col]):
        with col:
            st.markdown(f"### {side}耳")
            uploaded = st.file_uploader(f"{side}耳の写真をアップロード", type=["jpg", "jpeg", "png"], key=f"{selected_mouse}_{side}")
            if uploaded:
                file_path = os.path.join(mouse_folder, f"{selected_mouse}_{side}.jpg")
                img = Image.open(uploaded)
                img.save(file_path)
                st.image(img, caption=f"{selected_mouse}_{side}.jpg", use_container_width=True)
                st.success(f"{side}耳の写真を保存しました！")

    # 両耳が揃っているか確認
    left_file = os.path.join(mouse_folder, f"{selected_mouse}_左.jpg")
    right_file = os.path.join(mouse_folder, f"{selected_mouse}_右.jpg")

    if os.path.exists(left_file) and os.path.exists(right_file):
        st.success("✅ 両耳の写真が揃いました！")
else:
    st.info("まずマウスを登録してください。")

st.divider()

# --- ZIP ダウンロード ---
st.subheader("📦 本日分のデータをまとめてダウンロード")

today_str = datetime.now().strftime("%Y-%m-%d")
today_dir = os.path.join(BASE_DIR, today_str)

if os.path.exists(today_dir) and os.listdir(today_dir):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(today_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, today_dir))
    zip_buffer.seek(0)

    st.download_button(
        label=f"📥 {today_str} の写真をZIPでダウンロード",
        data=zip_buffer,
        file_name=f"mice_{today_str}.zip",
        mime="application/zip"
    )
else:
    st.info("まだ本日の写真データはありません。")
