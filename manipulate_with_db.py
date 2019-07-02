from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine  # make connection between class definitions and
							# tables without db
DBSession = sessionmaker(bind=engine)  # comunitacion between engine and execution
session = DBSession()

#### CREATE item ####
#create new restaurant
myFirstRestaurant = Restaurant(name="Pizza Palace")
session.add(myFirstRestaurant)
session.commit()

#create new menu item
cheesepizza = MenuItem(name="Cheese Pizza",
					   description="Made with natural ingredients",
					   course="Entree",
					   price="$8.99",
					   restaurant=myFirstRestaurant)
session.add(cheesepizza)
session.commit()

#### READ from db ####
firstResult = session.query(Restaurant).first()
firstResult.name

items = session.query(MenuItem).all()
for item in items:
	print(item.name)

#### UPDATE item ####
#search current item
veggieBurgers = session.query(MenuItem).filter_by(name='Veggie Burger')
for veggieBurger in veggieBurgers:
	print(veggieBurger.id)
	print(veggieBurger.price)
	print(veggieBurger.restaurant.name)
	print("\n")

#update current item
UrbanVeggieBurger = session.query(MenuItem).filter_by(id=2).one()
UrbanVeggieBurger.price = '$2.99'
session.add(UrbanVeggieBurger)
session.commit()

#### DELETE current item ####
spinach = session.query(MenuItem).filter_by(name='Spinach Ice Cream')
session.delete(spinach)
session.commit()
