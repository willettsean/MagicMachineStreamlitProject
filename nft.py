import streamlit as st
import requests
import json
from web3 import Web3
import pandas as pd


endpoint_choices = ['Assets', 'Events', 'Graphs']
endpoint = st.sidebar.selectbox("Endpoints:", endpoint_choices)

collection_choices = ['forgottenruneswizardscult', 'forgottensouls', 'SemiSupers']
collection = st.sidebar.selectbox("Choose Collection Slug:", collection_choices)


st.header(f"Magic Machine API Explorer - {endpoint}")
def render_asset(asset):
    st.subheader(f"{asset['name']} #{asset['token_id']}")
    st.image(asset['image_url'])


if endpoint == 'Events':
    event_type = st.sidebar.selectbox("Event Type",
                                      ['', 'successful', 'offer_entered', 'approve'])
    asset_contract_address = st.sidebar.text_input("Contract Address")
    token_id = st.sidebar.text_input("Token ID")

    params = {}
    if collection:
        params['collection_slug'] = collection
    if asset_contract_address:
        params['asset_contract_address'] = asset_contract_address
    if token_id:
        params['token_id'] = token_id
    if event_type:
        params['event_type'] = event_type

    if event_type == '':
        st.write("Insert an event type in the sidebar.")

    r = requests.get('https://api.opensea.io/api/v1/events', params=params)

    events = r.json()
    event_list = []
    for event in events['asset_events']:

        if event_type == 'offer_entered':
            if event['bid_amount']:
                bid_amount = Web3.fromWei(int(event['bid_amount']), 'ether')
            if event['from_account']['user']:
                bidder = event['from_account']['user']['username']
            else:
                bidder = event['from_account']['address']

            event_list.append([event['created_date'], bidder, float(bid_amount), event['asset']['name'],
                               event['asset']['token_id']])

        if event_type == 'successful':
            if event['total_price']:
                total_price = Web3.fromWei(int(event['total_price']), 'ether')
            if event['transaction']['from_account']['user']:
                buyer = event['transaction']['from_account']['user']['username']
            else:
                buyer = event['transaction']['from_account']['address']

            event_list.append([event['created_date'], buyer, float(total_price), event['asset']['name'],
                               event['asset']['token_id']])

    df = pd.DataFrame(event_list, columns=['time', 'buyer', 'total_price', 'name', 'token_id'])
    st.write(df)

    st.write(events)


if endpoint == 'Assets':
    st.sidebar.header('Filters')
    owner = st.sidebar.text_input("Owner")
    token_ids = st.sidebar.text_input("Token ID")

    params = {'owner': owner}

    if collection:
        params['collection'] = collection
    if token_ids:
        params['token_ids'] = token_ids


    r = requests.get('https://api.opensea.io/api/v1/assets', params=params)

    assets = r.json()['assets']
    for asset in assets:
        render_asset(asset)

    st.subheader("Raw JSON Data")
    st.write(r.json())

if endpoint == 'Graphs':
    event_type = 'successful'

    wizards = st.sidebar.checkbox("Wizards")
    souls = st.sidebar.checkbox("Souls")
    semis = st.sidebar.checkbox("Semis")

    params = {}
    if collection:
        params['collection_slug'] = collection
    if event_type:
        params['event_type'] = event_type

    if event_type == '':
        st.write("Insert an event type in the sidebar.")

    r = requests.get('https://api.opensea.io/api/v1/events', params=params)

    events = r.json()
    event_list = []
    for event in events['asset_events']:
        if event_type == 'successful':
            if event['total_price']:
                total_price = Web3.fromWei(int(event['total_price']), 'ether')
            event_list.append([event['created_date'], float(total_price), event['asset']['asset_contract']['name']])

    df = pd.DataFrame(event_list, columns=['time', 'total_price', 'collection'])
    st.write(df)
    st.line_chart(df)

    st.write(events)