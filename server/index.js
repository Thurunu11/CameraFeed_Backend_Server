const express = require('express');
const db_con = require("./sql_con");
const http = require('http');

// Importing dotenv module
require("dotenv").config();
const app = express();

PORT =process.env.PORT   //PORT allocated for the MySQL server

app.post(`/routeDataFromEsp32ToServer`,(request, response)=> {
    // Check if the request is a POST request
    if (request.method === 'POST') {
        let data1 = '';

        // Collect the data from the request
        request.on('data', chunk => {
            data1 += chunk;
        });

        // console.log(data1);

        // When all data has been collected
        request.on('end', () => {
            // Parse the data as JSON
            const { station1, image_data,current_val } = JSON.parse(data1);

            // Displaying the test data in the console
            // console.log(station1, image_data,current_val);

            // Write the acquired data in to the database
            const query1 = `INSERT INTO esp32camimage (Name2, visualdata) VALUES (?, ?)`;
            const values1 = [station1,  image_data];

            const query2 = `INSERT INTO thermalimage (Name1, thermaldata) VALUES (?, ?)`;
            const values2 = [station1,  current_val];


            // Execute the query
            db_con.query(query1, values1, (err, rows) => {
                if (err) {
                    console.log(err);
                } else {
                    console.log(" Visual Data inserted");
                }
            });

            db_con.query(query2, values2, (err, rows) => {
                if (err) {
                    console.log(err);
                } else {
                    console.log(" Thermal Data inserted");
                }
            });

            // Send a response to the NodeMCU
            response.writeHead(200, {'Content-Type': 'application/json'});
            response.end(' Visual Data received\n');
        });
    } else {
        // Send a 404 error if the request is not a POST request
        response.writeHead(404, {'Content-Type': 'text/plain'});
        response.end('Invalid request method\n');
    }
});

app.get(`/routeDataFromServerToClient/Thermal`,(req, res, response)=> {
    db_con.query("SELECT * FROM thermalimage", (error, data) => {
        if (error) {
            return res.json({ status: "ERROR", error });
        }

        return res.json(data);
    });
});

app.get(`/routeDataFromServerToClient/RGB`,(req, res, response)=> {
    db_con.query("SELECT * FROM esp32camimage", (error, data) => {
        if (error) {
            return res.json({ status: "ERROR", error });
        }

        return res.json(data);
    });
});



app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
}   );