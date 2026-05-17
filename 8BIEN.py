with tab2:
        if db["history"]:
            # Tạo danh sách dữ liệu để hiển thị bảng
            disp_list = []
            for h in db["history"][:50]: # Hiển thị 50 kỳ gần nhất
                s_val = h.get("Số", "00")
                bits = encode_8bit(s_val) # Hàm mã hóa 8 biến đã có ở các bản trước
                
                # Chuyển đổi bit thành ký hiệu L/C, T/B, Th/Kp theo đúng ảnh mẫu
                disp_list.append({
                    "Kỳ": int(h.get("Kỳ", 0)),
                    "Số": s_val,
                    "R": int(h.get("Rank", h.get("R_AI", 0))),
                    "Đ.CL": "L" if bits[0] else "C",
                    "Đu.CL": "L" if bits[1] else "C",
                    "T.CL": "L" if bits[2] else "C",
                    "Đ.TB": "T" if bits[3] else "B",
                    "Đu.TB": "T" if bits[4] else "B",
                    "T.TB": "T" if bits[5] else "B",
                    "Hệ": "Th" if bits[6] else "Kp",
                    "Hi.TB": "T" if bits[7] else "B"
                })
            
            # Hiển thị bảng dạng DataFrame chuẩn giao diện mobile
            df_display = pd.DataFrame(disp_list)
            st.dataframe(
                df_display, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Kỳ": st.column_config.NumberColumn(format="%d"),
                    "R": st.column_config.NumberColumn(format="%d")
                }
            )
