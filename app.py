import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import json
import time

# --- Helper Functions ---

@st.cache_data
def load_data():
    # Load the CSV data (this file is part of the extracted dataset)
    csv_path = "/mnt/data/ecommerce_dataset/ecommerce_dataset_updated.csv"
    df = pd.read_csv(csv_path)
    return df

def build_ontology_graph(df, sample_size=100):
    """Builds a sample ontology graph using NetworkX from a sample of the data."""
    # Sample the data for visualization to keep the graph manageable.
    sample_df = df.sample(n=min(len(df), sample_size), random_state=42)

    G = nx.Graph()
    # Add edges for each sample row:
    for idx, row in sample_df.iterrows():
        user = f"User: {row['User_ID'][:6]}"
        product = f"Product: {row['Product_ID'][:6]}"
        category = f"Category: {row['Category']}"
        paymeth = f"Payment: {row['Payment_Method']}"

        # Add nodes (they will be added automatically with edges, but this makes labels consistent)
        G.add_node(user, type="User")
        G.add_node(product, type="Product")
        G.add_node(category, type="Category")
        G.add_node(paymeth, type="PaymentMethod")

        # Relationships
        G.add_edge(user, product, relation="purchased")
        G.add_edge(product, category, relation="belongsTo")
        G.add_edge(user, paymeth, relation="paidWith")
        
    return G

def plot_graph(G):
    """Plot the ontology graph using matplotlib and NetworkX."""
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)
    # Draw nodes and edges
    nx.draw(G, pos, with_labels=True, node_size=500, font_size=8)
    return plt

def dataframe_to_csv_bytes(df):
    csv = df.to_csv(index=False)
    return csv.encode('utf-8')

def dataframe_to_json_bytes(df):
    json_data = df.to_json(orient='records')
    return json_data.encode('utf-8')

# Initialize session state for performance metrics and chat logs
if "agent_interactions" not in st.session_state:
    st.session_state.agent_interactions = []
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "total_response_time" not in st.session_state:
    st.session_state.total_response_time = 0.0
if "data" not in st.session_state:
    st.session_state.data = load_data()

# --- Sidebar Navigation ---
st.sidebar.title("Ontology Tool Demo")
page = st.sidebar.selectbox(
    "Select a feature",
    ("Ontology Overview", "Visualization", "Agent Chat", "Performance Dashboard", "Upload New Data", "Export Data")
)

# --- Page: Ontology Overview ---
if page == "Ontology Overview":
    st.title("Ontology Overview for Conversational BI")
    st.write("""
        This tool creates an ontology from e-commerce data intended for conversational BI using an LLM and a knowledge graph.
        The ontology captures key entities like **User**, **Product**, **Category**, and **PaymentMethod** with relationships:
        - **User** _purchased_ **Product**
        - **Product** _belongsTo_ **Category**
        - **User** _paidWith_ **PaymentMethod**
    """)
    
    df = st.session_state.data
    st.subheader("Data Snapshot")
    st.dataframe(df.head(10))
    
    st.subheader("Identified Entities")
    entities = {
        "Users": len(df["User_ID"].unique()),
        "Products": len(df["Product_ID"].unique()),
        "Categories": len(df["Category"].unique()),
        "Payment Methods": len(df["Payment_Method"].unique())
    }
    st.write(entities)
    
    st.subheader("Relationships")
    st.write("""
    - **User** → **Product**: Represents customer purchases.
    - **Product** → **Category**: Connects products to their category.
    - **User** → **PaymentMethod**: Denotes the payment method used for purchases.
    """)

# --- Page: Visualization ---
elif page == "Visualization":
    st.title("Ontology Graph Visualization")
    st.write("Below is a sample interactive network graph of the ontology (using a sample subset of data).")
    
    df = st.session_state.data
    G = build_ontology_graph(df)
    fig = plot_graph(G)
    st.pyplot(fig)
    
# --- Page: Agent Chat ---
elif page == "Agent Chat":
    st.title("LLM Agent Chat")
    st.write("Simulate conversational BI. Ask questions about the e-commerce data, and the agent will respond (this is a simulated response).")
    
    query = st.text_input("Enter your query:")
    if st.button("Submit Query"):
        if query.strip() == "":
            st.warning("Please enter a query.")
        else:
            start_time = time.time()
            st.write("Processing query...")
            time.sleep(1)  # Simulating a response delay
            response = f"Agent Response: You asked '{query}'. (This is a simulated response based on the ontology.)"
            st.write(response)
            # Log the interaction
            duration = time.time() - start_time
            st.session_state.agent_interactions.append({"query": query, "response": response, "response_time": duration})
            st.session_state.query_count += 1
            st.session_state.total_response_time += duration

    # Display recent interactions
    if st.session_state.agent_interactions:
        st.subheader("Recent Interactions")
        for interaction in st.session_state.agent_interactions[-5:]:
            st.markdown(f"**Q:** {interaction['query']}  \n**A:** {interaction['response']}  \n*Response Time: {interaction['response_time']:.2f} sec*")
            
# --- Page: Performance Dashboard ---
elif page == "Performance Dashboard":
    st.title("Performance Dashboard")
    st.write("Monitor the performance of the ontology tool and agent interactions.")
    
    query_count = st.session_state.query_count
    total_time = st.session_state.total_response_time
    avg_time = total_time / query_count if query_count else 0

    st.write(f"**Total Queries:** {query_count}")
    st.write(f"**Average Response Time:** {avg_time:.2f} seconds")
    
    # Simple performance chart
    st.subheader("Interaction Metrics")
    metrics = {
        "Total Queries": query_count,
        "Total Response Time (sec)": total_time,
        "Avg Response Time (sec)": avg_time
    }
    metric_names = list(metrics.keys())
    metric_values = list(metrics.values())
    
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.bar(metric_names, metric_values)
    ax2.set_ylabel("Value")
    ax2.set_title("Performance Metrics")
    st.pyplot(fig2)
    
# --- Page: Upload New Data ---
elif page == "Upload New Data":
    st.title("Upload / Update Data")
    st.write("Upload a CSV file to add more e-commerce data to the ontology.")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            new_data = pd.read_csv(uploaded_file)
            st.write("New data preview:")
            st.dataframe(new_data.head())
            # Append to current data
            st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
            st.success("Data has been updated successfully!")
        except Exception as e:
            st.error(f"Error uploading file: {e}")

# --- Page: Export Data ---
elif page == "Export Data":
    st.title("Export Ontology Data")
    st.write("Export the underlying e-commerce data in CSV or JSON format for integration with other tools.")
    df = st.session_state.data
    
    csv_bytes = dataframe_to_csv_bytes(df)
    json_bytes = dataframe_to_json_bytes(df)
    
    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name="ecommerce_ontology_data.csv",
        mime="text/csv"
    )
    
    st.download_button(
        label="Download JSON",
        data=json_bytes,
        file_name="ecommerce_ontology_data.json",
        mime="application/json"
    )
