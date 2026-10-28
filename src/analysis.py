"""第08讲 渠道、ROAS、ROI与获客成本
业务问题：哪个渠道值得加预算，哪些结论还不能下？
全部使用模拟教学数据。"""
from pathlib import Path
import sys
if "__file__" in globals():
    COURSE_ROOT = Path(__file__).resolve().parents[1]
else:
    COURSE_ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "course_common.py").exists())
if str(COURSE_ROOT) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from course_common import (ROOT, DATA, AS_OF, BLUE, TEAL, ORANGE, load_tables,
    build_facts, positive_orders, rfm_table, safe_divide, outdir, save_table, save_figure, show)

# %% 同一观察窗口，先分别聚合收入和费用再关联
t=load_tables();_,o=build_facts(t)
revenue=o.groupby('channel',as_index=False).agg(net_sales_cents=('net_sales_calc','sum'),contribution_cents=('contribution_cents','sum'))
spend=t['marketing'].groupby('channel',as_index=False).spend_cents.sum()
report=revenue.merge(spend,on='channel',validate='one_to_one')
first=positive_orders().sort_values(['order_date','order_id']).drop_duplicates('customer_id')
new=first.groupby('channel').customer_id.nunique().rename('new_buyers')
report=report.merge(new,on='channel',how='left',validate='one_to_one')
report['roas']=safe_divide(report.net_sales_cents,report.spend_cents)
report['contribution_roi']=safe_divide(report.contribution_cents-report.spend_cents,report.spend_cents)
report['cac_yuan']=safe_divide(report.spend_cents,report.new_buyers)/100
show(report);save_table(report,8,'channel_marketing')
assert report.loc[report.spend_cents.eq(0),'roas'].isna().all()
paid=report.loc[report.spend_cents.gt(0)]
fig,ax=plt.subplots(figsize=(7,4));ax.bar(paid.channel,paid.roas,color=TEAL)
ax.set(title='Attributed ROAS, paid channels only',ylabel='Net merchandise revenue / spend');save_figure(fig,8,'paid_channel_roas')
print('新客按观察期首次正净额订单归因；数据假定无期前历史。入口归因不是随机试验，不能据此认定增量效果。')
