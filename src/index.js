const fs = require('fs').promises;
const avro = require('avro-js');
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

// Function to read the schema from a file
async function readSchemaFromFile(filePath) {
    const data = await fs.readFile(filePath, {});
    return JSON.parse(data);
}

// Function to read and decode Avro data
async function readAvroData(schema, avroFilePath) {
    const dataBuffer = await fs.readFile(avroFilePath);
    const avroType = avro.parse(schema);
    return avroType.fromBuffer(dataBuffer);
}


app.get('/data', async (req, res) => {
    try {
        const pageSize = parseInt(req.query.pageSize, 10) || 10;
        const pageNumber = parseInt(req.query.pageNumber, 10) || 1;
        const filters = req.query.filters ? JSON.parse(req.query.filters) : {};

        // const schemaFilePath = 'crawlers/schema.avsc';
        // const avroFilePath = 'data/data.avro';

        // const schema = await readSchemaFromFile(schemaFilePath);
        // const data = await readAvroData(schema, avroFilePath);

        const schema = require('./crawlers/schema.avsc');
        const data = require('data/data.avro');
        const deserializedData = avro.deserialize(schema, data);


        // Implement your pagination and filtering logic here
        // For now, returning the raw data
        res.json(data);
    } catch (err) {
        console.error('Error:', err);
        res.status(500).send('Internal Server Error');
    }
});

const port = process.env.PORT || 8080;

app.listen(port, () => console.log(`app listening on http://localhost:${port}`));