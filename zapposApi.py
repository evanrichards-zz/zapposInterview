# Programmer: Evan Richards
# For Zappos Internship interview
# In order to facilitate better gift giving on the Zappos website, this
# 	script takes the desired number of products and the the desired amount
#	of money to spend and returns combinations of that many products whose
#	total is closest to that amount.

from urllib import urlopen
from sys import argv
from json import loads as jsonloads


def find_new_item(range_above_base, list_of_item_descriptions, base_price = 0):
	# This function does the API call and price adjustment. It takes the base
	# price that the function will not search for products below, which is
	# defaulted to zero. It takes the range above the base to start the search
	# and a list of descriptions of items that have already been added in order
	# to ensure diversity of products.
	
	# This tracks the number of requests we have attempted and changes the 
	# price based on that.
	num_requests = 0

	# The vast majority of items on Zappos end in 99 cents, so we will round 
	# down to closest 99 cent price
	ideal_price = range_above_base + base_price 
	if(ideal_price%1 != 0.99):
		ideal_price = int(ideal_price) - 0.01
	# This is how many items are returned from the API call per page
	items_per_page_num = 5
	# If all the items in a request are used, we increment this to get the 
	# next page
	page_num = 1
	# As long as our search is still within the range provided, keep looking
	while(ideal_price > base_price and num_requests <= 5):
		list_to_return = []
		# Base URL for call, we are searching for " " and letting the filters
		# do the work for us.
		base_request = "http://api.zappos.com/Search/term/%20?"
		# Part of the API call that deals with items per call and pagination
		item_limit = "&limit=" + str(items_per_page_num) + "&page="+ str(page_num)
		# Part of the API call that sets the price we are looking for
		facets = "&filters={%22price%22:[%22" + str(ideal_price) + "%22]}"
		# Sets how the items are returned to us. We want the most popular.
		sort = "&sort={%22productPopularity%22:%22desc%22}"
		# This is the API key that authorizes us to use Zappos' API
		api_key = "&key=52ddafbe3ee659bad97fcce7c53592916a6bfd73"
		# Piecing the parts together to form a complete call
		request = base_request + item_limit + facets + sort + api_key
		# Make the API call, read it, parse it as json into a hash.
		item = jsonloads(urlopen(request).read())
		num_requests = num_requests + 1
		# If the request was empty it doesn't have the key "results" and in some
		# cases it has results but no count, so we check for that too.
		if(item.has_key('results') and len(item['results']) != 0):
			for item_in_request in item['results']:
				# If we don't already have this item, add it to the list
				if item_in_request['productName'] not in list_of_item_descriptions:
					list_of_item_descriptions.append(item_in_request['productName'])
					list_to_return.append(item_in_request)
			# If we have something to return, do so
			if(len(list_to_return) != 0):
				return list_to_return
			# If we haven't found any new items, go to the next page
			page_num = page_num + 1

		# If we don't have any results, we need to change the price
		else:
			# Most items on Zappos end in 99 cents so, we will optimize
			# by just adjusting the price by whole dollars
			ideal_price = ideal_price - (1.0 * num_requests)
	return 0

# Holds the amount the user wants to spend
price = 0
# Holds the number of items the user wants to buy
num_items = 0
# This list holds the items to be purchased
list_of_items = []
# This holds the product name to campare against the other items we
# have found. It is faster than comparing the whole product description
# and ensures that we don't have any products with the same name but
# some other difference, such as color or style. This way we have 
# a diverse shopping list.
list_of_item_descriptions = []
# This is the total amount that has been spent so far
total_spent = 0
# This is the number of items found so far
total_items = 0


# Check to see if arguments were passed in through the 
# 	command line.
if(len(argv) == 3):
	# Use command line specified values
	first = int(float(argv[1])*100)
	second = int(float(argv[2])*100)
	if(first > second):
		# All monetary units are stored as cents to solve the 2 decimal
		# places in API search issue.
		price = first
		num_items = second / 100
	else: 
		price = second
		num_items = first/100
print """	This script makes gift shopping easy for you.
	Just enter the total amount of money you want to spend
	on gifts and the number of gifts you want purchased."""
while(num_items <= 0 or price <= 0):
	# If not, prompt user for them
	price = input('Total amount to spend for gifts: $')*100.0
	num_items = input('Number of items to purchase: ')
	if(num_items <= 0 or price <= 0):
		print "\nError: Please use only positive numbers.\n\n"
finished = False
while(not finished):
	# Ideally, we want items of all similar pricing, so we
	# start with this ideal price that calculates that
	ideal_price = ((price - total_spent) / (num_items - total_items))/100.0
	# Find anywhere from 1-4  new items that fit the budget
	items_found = find_new_item(ideal_price, list_of_item_descriptions)
	# Add them to list of items
	if(items_found == 0):
		print "Unable to find items in that price range."
		break
	for item in items_found:
		if(total_items != num_items):
			list_of_items.append(item)
			# Add its cost to total_spent
			item_price = float(item["price"][1:].replace(",",""))
			total_spent = total_spent + int(item_price*100)
			total_items = total_items + 1
			print "Found item number", total_items
	# Check to see if we can stop
	if(total_items == num_items):
		finished = True


# If we are off by at least a dollar from our total cost then
# try to find an item to replace one we already have with.
if(len(list_of_items) == total_items):
	money_left =  price-total_spent
	if(price - total_spent > 100):
		original_item_price = items_found[0]['price'][1:].replace(",","")
		original_item_price = float(original_item_price)
		final_item = find_new_item(money_left/100.0,
									list_of_item_descriptions, 
									original_item_price)
		if(final_item != 0):
			total_spent = total_spent - original_item_price*100 + \
					float(final_item[0]['price'][1:])*100
			list_of_items[0] = final_item[0]

	print "Spent $", total_spent/100.0, "of $", price/100.0
	for item in list_of_items:
		print item['brandName'], item['productName'], item['price']
		print "Buy at: ", item['productUrl']
