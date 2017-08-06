import logging

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Burrough Rift
def _toggle_misting(location_hud):
	location_hud.find_element_by_xpath(".//a[@class='mistButton']").click()

def _get_mist_count(location_hud):
	mist_quantity_text = location_hud.find_element_by_xpath(".//div[@class='mistQuantity']").text
	mist_count = mist_quantity_text.split('/')[0]
	return int(mist_count)

def _burrough_rift_check_status(location_hud):
	mist_count = _get_mist_count(location_hud)
	return {'mist_count': mist_count}

def _toggle_misting(location_hud):
	location_hud.find_element_by_xpath(".//a[@class='mistButton']").click()

def _burrough_rift_mist_toggle(location_hud, data):
	# No previous data, so can't make decision
	if data is None: 
		return 

	prev_mist_count = data.get('mist_count')
	mist_count = _get_mist_count(location_hud)
	logging.info("Mist count before={0}, after={1}".format(prev_mist_count, mist_count))

	canisters_count = location_hud.find_element_by_xpath(".//div[contains(@class, 'mistCanisters')]/div[@class='quantity']").text
	if canisters_count == 0:
		logging.info("No canister left. No action needed.")
		return

	# Don't start misting when we haven't collected enough mist canister
	if mist_count == 0 and canisters_count < 60:
		return 

	if (prev_mist_count > mist_count and mist_count <= 5) or mist_count == 0:
		logging.info("Start misting.")
		_toggle_misting(location_hud)
	elif (prev_mist_count < mist_count and mist_count >= 18) or mist_count == 20:
		logging.info("Stop misting.")
		_toggle_misting(location_hud)


BEFORE_HORN_HANDLER_MAP = {
	'riftBurroughsHud': _burrough_rift_check_status
}

AFTER_HORN_HANDLER_MAP = {
	'riftBurroughsHud': _burrough_rift_mist_toggle
}

# Common util
def _find_hud(driver):
	try:
		location_hud = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='hudLocationContent']/div")))
		return (location_hud.get_attribute('class'), location_hud)
	except TimeoutException:
		return (None, None)

def _handle_hud_before_horn(location_class, location_hud):
	classes = location_class.split()
	handler = filter(
		lambda x: x is not None, 
		map(lambda c: BEFORE_HORN_HANDLER_MAP.get(c), classes),
	)
	if len(handler) > 0:
		data = handler[0](location_hud)
		data['location_class'] = location_class
		return data 
	return {'location_class': location_class} 

def _handle_hud_after_horn(location_class, location_hud, data):
	classes = location_class.split()
	handler = filter(
		lambda x: x is not None, 
		map(lambda c: AFTER_HORN_HANDLER_MAP.get(c), classes),
	)
	if len(handler) > 0:
		handler[0](location_hud, data)

# Main	
def before_horn(driver):
	location_class, location_hud = _find_hud(driver)
	data = _handle_hud_before_horn(location_class, location_hud)
	return data

def after_horn(driver, data):
	location_class, location_hud = _find_hud(driver)

	actual_data = dict()
	if location_class == data.get('location_class'):
		actual_data = data

	_handle_hud_after_horn(location_class, location_hud, actual_data)
