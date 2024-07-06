import streamlit as st
import pandas as pd
import pulp 
from src.shift_scheduler.ShiftScheduler import ShiftScheduler

st.title('シフトスケジューリングアプリ')

st.sidebar.header('データのアップロード')


calendar_file = st.sidebar.file_uploader('カレンダー', type=['csv'])
staff_file = st.sidebar.file_uploader('スタッフ', type=['csv'])

tab1, tab2, tab3 = st.tabs(['カレンダー情報', 'スタッフ情報', 'シフト表作成'])

with tab1:
	if calendar_file is None:
		st.write('カレンダー情報をアップロードしてください')
	else:
		st.markdown('## カレンダー情報')
		calendar_data = pd.read_csv(calendar_file)
		st.table(calendar_data)

with tab2:
	if staff_file is None:
		st.write('スタッフ情報をアップロードしてください')
	else:
		st.markdown('## スタッフ情報')
		staff_data = pd.read_csv(staff_file)
		st.table(staff_data)

with tab3:
	if staff_file is None:
		st.write('スタッフ情報をアップロードしてください')
	if calendar_file is None:
		st.write('カレンダー情報をアップロードしてください')
	if staff_file is not None and calendar_file is not None:
		optimize_button = st.button('シフト作成')
		if optimize_button:
			ss = ShiftScheduler()
			ss.set_data(staff_data, calendar_data)
			ss.build_model()
			ss.solve()

			st.markdown('## 最適化結果')
			st.write('status:', pulp.LpStatus[ss.status])
			st.write('objective:', ss.model.objective.value())

			st.markdown('## シフト表')
			st.table(ss.sch_df)

			st.markdown('## シフト数の充足確認')
			shift_sum = ss.sch_df.sum(axis=1)
			st.bar_chart(shift_sum)

			st.markdown('## スタッフ数の充足確認')
			shift_sum_slot = ss.sch_df.sum(axis=0)
			st.bar_chart(shift_sum_slot)

			st.markdown("## 責任者の合計シフト数の充足確認")
			shift_schedule_with_staff_data = pd.merge(ss.sch_df, staff_data, left_index=True, right_on="スタッフID")

			shift_chief_only = shift_schedule_with_staff_data.query("責任者フラグ == 1")
			shift_chief_only = shift_chief_only.drop(columns=["スタッフID","責任者フラグ","希望最小出勤日数","希望最大出勤日数"])
			shift_chief_sum = shift_chief_only.sum(axis=0)
			st.bar_chart(shift_chief_sum)


			# シフト表のダウンロード
			st.download_button(label="シフト表をダウンロード"
				, data=ss.sch_df.to_csv().encode("utf-8")
				, file_name="output.csv"
				, mime="text/csv")

		#st.markdown('## 最適化結果')
		#st.markdown('## スタッフの希望の確認')
		#st.markdown('## 責任者の合計シフト数の充足確認')



