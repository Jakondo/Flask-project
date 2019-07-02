from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import sys

from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


#create session and connetc to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		try:
			''' Page for creating a New Restaurant'''
			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body>"
				output += "<h1> Make a NEW Restaurant </h1>"
				output += "<form method='POST' enctype='multipart/form-data' " \
						  "action='/restaurants/new'>"
				output += "<input name='newRestaurantName' type='text' " \
						  "placeholder='New Restaurant Name'>"
				output += "<input type='submit' value='Create'>"
				output += "</form></html></body>"
				self.wfile.write(output.encode("utf-8"))
				return

			'''Editing page'''
			if self.path.endswith("/edit"):
				restaurantIDPath = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(
					id=restaurantIDPath).one()
				if myRestaurantQuery:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = ""
					output += "<html><body>"
					output += "<h1>"
					output += myRestaurantQuery.name
					output += "</h1>"
					output += "<form method='POST' " \
							  "enctype='multipart/form-data' " \
							  "action='/restaurants/%s/edit'>" % \
							  restaurantIDPath
					output += "<input name = 'newRestaurantName' type='text' " \
							  "placeholder='%s'>" % myRestaurantQuery.name
					output += "<input type='submit' value='Rename'>"
					output += "</form>"
					output += "</body></html>"

					self.wfile.write(output.encode("utf-8"))


			'''Delete page'''
			if self.path.endswith("/delete"):
				restaurantIDPath = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(
					id=restaurantIDPath).one()
				if myRestaurantQuery:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = ""
					output += "<html><body>"
					output += "<h1>"
					output += myRestaurantQuery.name
					output += "</h1>"
					output += "<a href = '/restaurants'> <input type='submit' " \
							  "value='Go Back'> </a><p>"
					output += "<form method='POST' " \
							  "enctype='multipart/form-data' " \
							  "action='/restaurants/%s/delete'>" % \
							  restaurantIDPath
					output += "<input type='submit' value='Delete'>"
					output += "</form>"
					output += "</body></html>"

				self.wfile.write(output.encode("utf-8"))


			'''Page with list of all restaurants'''
			if self.path.endswith("/restaurants"):
				restaurants = session.query(Restaurant).all()
				output = ""
				#Link to page with CREATING form
				output += "<a href='/restaurants/new'> Make a NEW Restaurants Here </a></br></br>"

				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output += "<html><body>"
				for restaurant in restaurants:
					output += restaurant.name
					output += "</br> <a href= '/restaurants/%s/edit'> Edit " \
							  "</a> " % restaurant.id
					output += "<a href= '/restaurants/%s/delete'> Delete " \
							  "</a>" % restaurant.id
					output += "</br></br></br>"

				output += "</body></html>"
				self.wfile.write(output.encode("utf-8"))
				return

			if self.path.endswith("/menu"):
				items = session.query(MenuItem).all()
				output = ""
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output += "<html><body>"
				for item in items:
					output += item.name
					output += "</br> <a href= #> Edit </a> <a href= #> Delete </a>"
					output += "</br></br></br>"

				output += "</body></html>"
				self.wfile.write(output.encode("utf-8"))
				return

		except IOError:
			self.send_error(404, 'File Not Found: %s' % self.path)

	def do_POST(self):
		try:
			if self.path.endswith("/restaurants/new"):
				ctype, pdict = cgi.parse_header(self.headers.get(
					'content-type'))
				pdict['boundary'] = pdict['boundary'].encode("utf-8")
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('newRestaurantName')

					# Create new Restaurant Object
					newRestaurant = Restaurant(name=messagecontent[0].decode(
						"utf-8"))
					session.add(newRestaurant)
					session.commit()

					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()

			if self.path.endswith("/delete"):
				restaurantIDPath = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(
					id=restaurantIDPath).one()
				if myRestaurantQuery:
					session.delete(myRestaurantQuery)
					session.commit()

					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()

			if self.path.endswith("/edit"):
				ctype, pdict = cgi.parse_header(self.headers.get(
					'content-type'))
				pdict['boundary'] = pdict['boundary'].encode("utf-8")
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('newRestaurantName')
					restaurantIDPath = self.path.split("/")[2]
					myRestaurantQuery = session.query(Restaurant).filter_by(
						id=restaurantIDPath).one()

					# Edit Restaurant Object
					if myRestaurantQuery != []:
						myRestaurantQuery.name = messagecontent[0].decode(
							"utf-8")
						session.add(myRestaurantQuery)
						session.commit()

						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						self.send_header('Location', '/restaurants')
						self.end_headers()

		except:
			self.send_error(404, "{}".format(sys.exc_info()[0]))
			print(sys.exc_info())


def main():
	try:
		server = HTTPServer(('', 8080), webServerHandler)
		print('web server running... open localhost:8080/restaurants in your browser')
		server.serve_forever()
	except KeyboardInterrupt:
		print('^C received, shutting down server')
		server.socket.close()


if __name__ == '__main__':
	main()
