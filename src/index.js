const fs = require('fs');

const app = require('express')();

// Path to your JSON file
const jsonFilePath = './data/blades/master_data.json';

// Pagination function
function paginate(array, pageSize, pageNumber) {
    const start = (pageNumber - 1) * pageSize;
    const end = pageNumber * pageSize;
    return array.slice(start, end);
}

// Filter function
function filterData(data, filters) {
    return data.filter(item => {
        let isValid = true;
        for (let key in filters) {
            if (item[key] !== filters[key]) {
                isValid = false;
                break;
            }
        }
        return isValid;
    });
}

// Endpoint to get paginated and filtered data
app.get('/data', (req, res) => {
    const pageSize = parseInt(req.query.pageSize) || 10;
    const pageNumber = parseInt(req.query.pageNumber) || 1;
    const filters = req.query.filters ? JSON.parse(req.query.filters) : {};

    fs.readFile(jsonFilePath, 'utf8', (err, data) => {
        if (err) {
            return res.status(500).send("Error reading file");
        }
        try {
            let jsonData = JSON.parse(data);
            // jsonData = filterData(jsonData, filters);
            const paginatedData = paginate(jsonData["revspin_data"], pageSize, pageNumber);
            res.json(paginatedData);
        } catch (err) {
            res.status(500).send("Error parsing JSON");
        }
    });
});

const port = process.env.PORT || 8080;

app.listen(port, () => console.log(`app listening on http://localhost:${port}`));