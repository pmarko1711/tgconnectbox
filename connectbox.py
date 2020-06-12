from connect_box import ConnectBox
import asyncio, aiohttp

async def get_cmstatus(host, password):
    async with aiohttp.ClientSession() as session:
        client = ConnectBox(session=session, host=host, password=password)
        await client.async_get_cmstatus_and_service_flows()
        await client.async_close_session()
        return {
            'cmstatus': client.cmstatus,
            'downstream_service_flows': client.downstream_service_flows,
            'upstream_service_flows': client.upstream_service_flows
        }

async def get_devices(host, password):
    async with aiohttp.ClientSession() as session:
        client = ConnectBox(session=session, host=host, password=password)
        await client.async_get_devices()
        await client.async_close_session()
        return client.devices


async def get_downstream(host, password):
    async with aiohttp.ClientSession() as session:
        client = ConnectBox(session=session, host=host, password=password)
        await client.async_get_devices()
        await client.async_close_session()
        return client.devices


async def get_upstream(host, password):
    async with aiohttp.ClientSession() as session:
        client = ConnectBox(session=session, host=host, password=password)
        await client.async_get_upstream()
        await client.async_close_session()
        return client.us_channels


async def get_temperature(host, password):
    async with aiohttp.ClientSession() as session:
        client = ConnectBox(session=session, host=host, password=password)
        await client.async_get_temperature()
        await client.async_close_session()
        return client.temperature


async def get_ipv6filters(host, password):
    async with aiohttp.ClientSession() as session:
        client = ConnectBox(session=session, host=host, password=password)
        await client.async_get_ipv6_filtering()
        await client.async_close_session()
        return client.ipv6_filters


async def toggle_ipv6filter(host, password, idd):
    async with aiohttp.ClientSession() as session:
        client = ConnectBox(session=session, host=host, password=password)
        new_value = await client.async_toggle_ipv6_filter(idd)
        await client.async_close_session()
        return new_value
