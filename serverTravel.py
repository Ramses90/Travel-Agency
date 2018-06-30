import socket
import threading
import sys
import pickle
import json


class Server():

    locked = False
    number_of_columns = 2
    number_of_seats_per_column = 24

    def __init__(self, host="localhost", port=10000):

        self.client = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((str(host), int(port)))
        self.sock.listen(10)
        self.sock.setblocking(True)  # Should be a blocking connection
        self.prompt = '\nFlight Booking Options: \n\nLIST/l | SEARCHD DEST/sd | SEARCHALL DEST/all | SEARCHS DEPARTURE/sdp | BUY_TICKETS/b | EXIT/exit:'

        self.acceptCon()
        # This function runs indefinitely
        # It keeps on accepting & then initializing server code for connections

    def take_input(self, client, prompt):


        client.send(pickle.dumps(prompt))

        client_response = ''  # Initialize response variable
        # Wait indefinitely until a response is seen using blocking connection
        while client_response is None or len(client_response) == 0:
            client_response = client.recv(1024*2)

        # Parse the response
        client_response = pickle.loads(client_response)

        return client_response

    def msg_to_all(self, msg, cliente):
        for c in self.client:
            try:
                if c != cliente:
                    c.send(msg)
            except:
                self.client.remove(c)

    def processCon(self, connection):

        c = connection
        response = self.take_input(
            client=c,
            prompt=self.prompt
        )

        print("Received ", response)
        #while response != 'stop':
        while True:
            if response == 'l':
                self.listAll(client=c)
            elif response == 'sd':
                self.searchd(client=c)
            elif response == 'all':
                self.searchalld(client=c)
            elif response == 'sdp':
                self.depart(client=c)
            elif response == 'b':
                res = self.yourOrigin(client=c)
                des = self.buyTickets(client=c)
                inputs = self.take_input(
                    client=c,
                    prompt="Would you like to buy a return ticket? yes/cancel"
                )
                if inputs == 'yes':
                    self.returnTickets(res,des, client =c)
                else:
                    prompt = "ENJOY YOUR FLIGHT!"
                    connection.send(pickle.dumps(prompt))

            elif response == 'exit':
                self.sock.close()
                sys.exit()

            
            response = self.take_input(
                client=c,
                prompt=self.prompt
            )


    def acceptCon(self):

        print("Connection has been established")

        while True:
            try:
                conn, saddr = self.sock.accept()
                conn.setblocking(True)
                self.client.append(conn)

                handler = threading.Thread(
                    target=self.processCon,
                    kwargs={"connection": conn}
                )
                handler.daemon = True
                handler.start()
            except:
                pass

     
    def asnSeats(self, client, seat):

        while not self.locked:
            self.locked = True  # First lock the file for your use

        count = 0
        for i in range(len(seat)):
            for j in range(len(seat[i])):
                if(seat[i][j] == 0):
                    count = count + 1
        
        return count


    #This function will list all the flights avaibles
    def listAll(self, client):

        with open('flightsdata.json') as f:
            data = json.load(f)

        response = ''

        for state in data['cities']:
            varn = ('-'.join(state['name'])) 
            varn3 = ('-'.join(reversed(state['name'])))
            price2 = state['price']
            seats3 = state['seats']
            priceperseats1 = ' '+ str(self.asnSeats(client,seats3)) +' '+ str(price2)
            response += varn + priceperseats1 +'\n'+ varn3 + priceperseats1 + '\n'
        
        client.send(pickle.dumps(response))

# This Function will search an ALLDEstination    
    def searchalld(self, client):

        ans = self.take_input(
            client=client,
            prompt='\nSearch Flights Destinations: '
        )

        with open('flightsdata.json') as f:
            data = json.load(f)

        response = 'ORIGEN | DESTINATION | SEATS | PRICE\n'
        for state in data['cities']:

            price1 = state['price']
            seats = state['seats']
            priceperseats = ' '+ str(self.asnSeats(client,seats)) +' '+ str(price1)
            if state['name'][1] == ans:
                destination1 = ('-'.join(state['name'])) + priceperseats + '\n' + ('-'.join(reversed(state['name']))) + priceperseats+'\n'

                response += destination1 
            
        client.send(pickle.dumps(response))
# This Function will search an specific destination example: MIA
    def searchd(self, client):

        ans = self.take_input(
            client=client,
            prompt='\nSearch Flights Destinations: '
        )

        with open('flightsdata.json') as f:
            data = json.load(f)

        response = 'ORIGEN | DESTINATION | SEATS | PRICE\n'
        for state in data['cities']:

            price1 = state['price']
            seats = state['seats']

            if state['name'][1] == ans:
                destination1 = ('-'.join(state['name']))

                response += destination1 + ' '+ str(self.asnSeats(client,seats)) +' '+ str(price1)+'\n'
            
        client.send(pickle.dumps(response))


    def yourOrigin(self, client):

        ans = self.take_input(
            client=client,
            prompt='\nPlease enter your Origin: '
        )        

        with open('flightsdata.json') as f:
            data = json.load(f)

        response = 'ORIGEN | DESTINATION | SEATS | PRICE\n'
        
        for state in data['cities']:
            price1 = state['price']
            seats = state['seats']

            if state['name'][0] == ans:
                destination1 = ('-'.join(state['name']))

                response += destination1 + ' '+ str(self.asnSeats(client,seats)) +' '+ str(price1)+'\n'
            
        client.send(pickle.dumps(response))
        return ans



    def depart(self, client):

        ans = self.take_input(
            client=client,
            prompt='\nSearch Flights Departures: '
        )

        with open('flightsdata.json') as f:
            data = json.load(f)

        response = 'ORIGEN | DESTINATION | SEATS | PRICE\n'
        for state in data['cities']:

            price1 = state['price']
            seats = state['seats']

            if state['name'][0] == ans:
                destination1 = ('-'.join(state['name']))

                response += destination1 + ' '+ str(self.asnSeats(client,seats)) +' '+ str(price1)+'\n'
            
        client.send(pickle.dumps(response))

#buy ticketts workinggg on 

    def buyTickets(self, client):

        where = self.take_input(
            client=client,
            prompt="\nEnter a destination for booking"
        )

        seat = self.take_input(
            client=client,
            prompt="\nEnter a seat number for booking"
        )
        seat = int(seat)

        while not self.locked:
            self.locked = True  # First lock the file for your use

            # Now read the data
        with open("flightsdata.json") as f:
            data = json.load(f)

        for state in data["cities"]:
            destination = state['name'][1]
            seats = state['seats']

            if where == destination:
                seats = self.asnSeats(client,seats)

                while True:

                    my_flight_data = state
                    row = int((seat - 1) / self.number_of_seats_per_column)
                    column = (seat - 1) % self.number_of_seats_per_column
                    print(row)
                    print(column)

                    if my_flight_data["seats"][column][row] == 0:
                        my_flight_data["seats"][column][row] = 1  # Buying ticket
                        response = "Seat %d booked successfully!" % seat
                        break
                    else:
                        inputs = self.take_input(
                            client=client,
                            prompt="Seat %d is not available." % seat + "Please choose another seat or Press cancel to Exit "
                        )
                        seat = int(inputs)
                        if inputs == 'cancel':
                            break
                    
                #data.pop(state)
                break

        with open('flightsdata.json', 'w') as outfile:
            json.dump(data, outfile)

        self.locked = False  # Unlocking for other threads

        client.send(pickle.dumps(response))

        return where


    def returnTickets(self, org, dest, client):

        seat = self.take_input(
            client=client,
            prompt="\nEnter a seat number for return flight back to" + org
        )
        seat = int(seat)

        while not self.locked:
            self.locked = True  # First lock the file for your use

            # Now read the data
        with open("flightsdata.json") as f:
            data = json.load(f)

        for state in data["cities"]:
            original = state['name'][0]
            fromComing = state['name'][1]
            seats = state['seats']

            if org == original and dest == fromComing:
                seats = self.asnSeats(client,seats)

                while True:

                    my_flight_data = state
                    row = int((seat - 1) / self.number_of_seats_per_column)
                    column = (seat - 1) % self.number_of_seats_per_column

                    if my_flight_data["seats"][column][row] == 0:
                        my_flight_data["seats"][column][row] = 1  # Buying ticket
                        response = "Seat %d booked successfully!" % seat
                        break
                    else:
                        inputs = self.take_input(
                            client=client,
                            prompt="Seat %d is not available." % seat + "Please choose another seat or Press cancel to Exit "
                        )
                        seat = int(inputs)

                        if inputs == 'cancel':
                            break
                    
                #data.pop(state)
                break

        with open('flightsdata.json', 'w') as outfile:
            json.dump(data, outfile)

        self.locked = False  # Unlocking for other threads

        client.send(pickle.dumps(response))



s = Server()
