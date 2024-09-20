import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from babel.numbers import format_currency

sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    return daily_orders_df


def create_sum_spend_df(df):
    sum_spend_df = df.resample(rule='D', on='order_approved_at').agg({
        "payment_value": "sum"
    })
    sum_spend_df = sum_spend_df.reset_index()
    sum_spend_df.rename(columns={
        "payment_value": "total_spend"
    }, inplace=True)

    return sum_spend_df


def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english")["product_id"].count().reset_index()
    sum_order_items_df.rename(columns={
        "product_id": "product_count"
    }, inplace=True)
    sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)

    return sum_order_items_df


def review_score_df(df):
    review_scores = df['review_score'].value_counts().sort_values(ascending=False)
    most_common_score = review_scores.idxmax()

    return review_scores, most_common_score


def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
    bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

    return bystate_df, most_common_state


def create_order_status(df):
    order_status_df = df["order_status"].value_counts().sort_values(ascending=False)
    most_common_status = order_status_df.idxmax()

    return order_status_df, most_common_status

def plot_brazil_map(data, plt, mpimg, urllib, st):
    # Load the Brazil map image from the URL
    brazil = mpimg.imread(
        urllib.request.urlopen('https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'),
        'jpg')

    # Create the scatter plot on top of the Brazil map
    fig, ax = plt.subplots(figsize=(10, 10))  # Adjust the figure size as needed
    ax = data.plot(kind="scatter", x="geolocation_lng", y="geolocation_lat", figsize=(10, 10), alpha=0.3,
                   s=0.3, c='maroon', ax=ax)  # Customize marker size and color

    # Hide axis
    ax.axis('off')

    # Overlay the map image
    ax.imshow(brazil, extent=[-73.98283055, -33.8, -33.75116944, 5.4])

    # Display the plot in Streamlit
    st.pyplot(fig)


# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date",
                 "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("all_data.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

# Geolocation Dataset
geolocation = pd.read_csv('../data/geolocation.csv')
data = geolocation.drop_duplicates(subset='customer_unique_id')

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    # Title
    st.title("Fan Fan Firgiawan")

    # Menambahkan logo perusahaan
    st.image("logo.png")

    # Date Range
    start_date, end_date = st.date_input(
        label="Pilih Tanggal",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Main
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) &
                 (all_df["order_approved_at"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_spend_df = create_sum_spend_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
review_score, common_score = review_score_df(main_df)
state, most_common_state = create_bystate_df(main_df)
order_status, common_status = create_order_status(main_df)

# Title
st.header("E-Commerce Dashboard :sparkles:")

# Daily Orders
st.subheader("Pesanan Harian")

col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Pendapatan: **{total_revenue}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Customer Spend Money
st.subheader("Pelangan Menghabiskan Uang")
col1, col2 = st.columns(2)

with col1:
    total_spend = format_currency(sum_spend_df["total_spend"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Pengeluaran: **{total_spend}**")

with col2:
    avg_spend = format_currency(sum_spend_df["total_spend"].mean(), "IDR", locale="id_ID")
    st.markdown(f"Rata-rata Pengeluaran: **{avg_spend}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    sum_spend_df["order_approved_at"],
    sum_spend_df["total_spend"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Order Items
st.subheader("Pesanan Barang")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Barang: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Rata-rata Barang: **{avg_items}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

colors = ["#068DA9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors,
            ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Produk paling banyak terjual", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="product_count", y="product_category_name_english",
            data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk paling sedikit terjual", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# Review Score
st.subheader("Ulasan")
col1, col2 = st.columns(2)

with col1:
    avg_review_score = review_score.mean()
    st.markdown(f"Rata-rata Skor Ulasan: **{avg_review_score}**")

with col2:
    most_common_review_score = review_score.value_counts().index[0]
    st.markdown(f"Skor Ulasan Paling Umum: **{most_common_review_score}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=review_score.index,
            y=review_score.values,
            order=review_score.index,
            palette=["#068DA9" if score == common_score else "#D3D3D3" for score in review_score.index]
            )

plt.title("Rating by customers for service", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Count")
plt.xticks(fontsize=12)
st.pyplot(fig)

# Customer Demographic
st.subheader("Demografi Pelangan")
tab1, tab2, tab3 = st.tabs(["State", "Order Status", "Geolocation"])

with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"Negara Paling Umum: **{most_common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index,
                y=state.customer_count.values,
                data=state,
                palette=["#068DA9" if score == most_common_state else "#D3D3D3" for score in
                         state.customer_state.value_counts().index]
                )

    plt.title("Nomor Pelanggan dari Negara Bagian", fontsize=15)
    plt.xlabel("Negara")
    plt.ylabel("Nomor Pelangan")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

with tab2:
    common_status_ = order_status.value_counts().index[0]
    st.markdown(f"Status Pesanan Paling Umum: **{common_status_}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=order_status.index,
                y=order_status.values,
                order=order_status.index,
                palette=["#068DA9" if score == common_status else "#D3D3D3" for score in order_status.index]
                )

    plt.title("Order Status", fontsize=15)
    plt.xlabel("Status")
    plt.ylabel("Count")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

with tab3:
    plot_brazil_map(data, plt, mpimg, urllib, st)

    with st.expander("Selengkapnya ...."):
        st.write(
            """
            Profil Demografis Pelanggan: Sebagian besar pelanggan berasal dari wilayah tenggara Brasil, terutama dari kota São Paulo dan negara bagian São Paulo. Wilayah lain yang memiliki jumlah pelanggan signifikan termasuk Rio de Janeiro, Minas Gerais, dan beberapa negara bagian di bagian selatan Brasil. Perbedaan Preferensi Pembelian: Meskipun grafik yang diberikan tidak secara langsung menunjukkan preferensi pembelian berdasarkan kelompok demografis, distribusi geografis ini menunjukkan bahwa pelanggan di wilayah tenggara dan selatan Brasil adalah pasar terbesar untuk platform e-commerce ini.

Mungkin ada perbedaan preferensi antara wilayah, tetapi data ini lebih menyoroti jumlah pelanggan daripada jenis produk yang mereka beli. Data tambahan tentang preferensi produk atau kelompok usia mungkin diperlukan untuk menganalisis preferensi pembelian lebih lanjut.

Secara keseluruhan, demografis pelanggan sangat terkonsentrasi di wilayah tenggara Brasil, dengan São Paulo sebagai kota dan negara bagian dengan jumlah pelanggan terbesar.
            """)
st.caption('Copyright (C) Fan Fan Firgiawan. 2024')
