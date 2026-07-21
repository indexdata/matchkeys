// matchkey for ISBN/ISSN and normalize terms for searching via CQL on SRU

function loadMarcJson(record) {
  const marcObj = JSON.parse(record).marc;
  if (marcObj.fields === undefined) {
    throw new Error('MARC fields array is missing.');
  }
  if (!Array.isArray(marcObj.fields)) {
    throw new Error('MARC fields is not an array.');
  }
  if (!marcObj.leader) {
    marcObj.leader = '00000nam a22000000a 4500';
  }
  return marcObj;
}

function getRelevantSubFields(record, tag, sf) {
  let data = [];
  const fields = record.fields.filter((f) => f[tag]);
  for (let x = 0; x < fields.length; x += 1) {
    const f = fields[x];
    if (f[tag].subfields) {
      for (let n = 0; n < f[tag].subfields.length; n += 1) {
        const s = f[tag].subfields[n];
        if (s[sf]) {
          data.push(s[sf]);
        }
      }
    }
  }
  if (data.length === 0) {
    return null;
  }
  return data;
}

/**
 * Share-VDE Works match key generation function. Takes a MARC-in-JSON record as input and generates
 * a match key string based on the 996 fields.
 * @param {string} record - The MARC-in-JSON input string wrapped in {marc: ...} object.
 * @return {array} String containing the works URI from 996$9
 */
export function matchkey(record) {
  const marcObj = loadMarcJson(record);

  let uris = getRelevantSubFields(marcObj, '996', '9');
  if (uris) {
    for (let n = 0; n < uris.length; n += 1) {
      uris = uris.filter((u) => u.match(/works|instances/));
    }
    return uris;
  }
}
