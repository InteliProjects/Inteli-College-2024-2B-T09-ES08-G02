import { useState } from 'react';
import { blockchain_integridad_backend } from 'declarations/blockchain-integridad-backend';

function App() {
  const [hash1, setHash1] = useState('');
  const [hash2, setHash2] = useState('');
  const [comparisonResult, setComparisonResult] = useState('');
  const [jsonContent, setJsonContent] = useState(null);
  const [editedContent, setEditedContent] = useState('');
  const [rawData, setRawData] = useState('');
  const [postResponse, setPostResponse] = useState('');

  async function handleCompare(event) {
    event.preventDefault();
    try {
      const result = await blockchain_integridad_backend.compare_hashes(hash1, hash2);
      if ("ok" in result) {
        setComparisonResult(`Resultado: ${result.ok}`);
      } else if ("err" in result) {
        setComparisonResult(`Erro: ${result.err}`);
      }
    } catch (error) {
      setComparisonResult(`Erro na comparação: ${error.message}`);
    }
    return false;
  }

  async function handleFileUpload1(event) {
    const file = event.target.files[0];
    if (file && file.type === "application/json") {
      const fileContents = await file.text();
      try {
        const parsedJSON = JSON.parse(fileContents);
        setJsonContent(parsedJSON);
        setEditedContent(parsedJSON.content || '');

        const hash = await generateHash(JSON.stringify(parsedJSON));
        setHash1(hash);
      } catch (error) {
        alert("Arquivo JSON inválido.");
      }
    } else {
      alert("Por favor, selecione um arquivo .json válido.");
    }
  }

  async function handleFileUpload2(event) {
    const file = event.target.files[0];
    if (file && file.type === "application/json") {
      const fileContents = await file.text();
      try {
        const parsedJSON = JSON.parse(fileContents);
        const hash = await generateHash(JSON.stringify(parsedJSON));
        setHash2(hash);
      } catch (error) {
        alert("Arquivo JSON inválido.");
      }
    } else {
      alert("Por favor, selecione um arquivo .json válido.");
    }
  }

  async function generateHash(content) {
    const encoder = new TextEncoder();
    const data = encoder.encode(content);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex;
  }

  async function handleSaveContent() {
    if (jsonContent) {
      const updatedJSON = { ...jsonContent, content: editedContent };
      setJsonContent(updatedJSON);
      const updatedHash = await generateHash(JSON.stringify(updatedJSON));
      setHash1(updatedHash);
      alert("Conteúdo atualizado com sucesso e hash regenerado!");
    }
  }

  async function fetchRawData(url) {
    try {
      const data = await blockchain_integridad_backend.get_raw_data(url);
      setRawData(data);
    } catch (error) {
      alert(`Erro ao buscar dados brutos: ${error.message}`);
    }
  }

  async function fetchStableRawJson() {
    try {
      const stableData = await blockchain_integridad_backend.get_stable_raw_json();
      alert(`Dados estáveis recuperados: ${stableData}`);
    } catch (error) {
      alert(`Erro ao recuperar dados estáveis: ${error.message}`);
    }
  }

  async function sendPostRequest(url, input) {
    try {
      const response = await blockchain_integridad_backend.send_post_request(url, input);
      setPostResponse(response);
    } catch (error) {
      alert(`Erro no envio do POST: ${error.message}`);
    }
  }

  return (
    <main>
      <h2>Faça upload do primeiro arquivo</h2>
      <input type="file" accept=".json" onChange={handleFileUpload1} />
      <section>
        <p>Hash do primeiro arquivo:</p>
        <p>{hash1}</p>
      </section>

      {jsonContent && (
        <section>
          <h3>Editar campo "content" do JSON:</h3>
          <textarea
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            rows="5"
            cols="50"
          />
          <br />
          <button onClick={handleSaveContent}>Salvar Alterações</button>
        </section>
      )}

      <h2>Faça upload do segundo arquivo</h2>
      <input type="file" accept=".json" onChange={handleFileUpload2} />
      <section>
        <p>Hash do segundo arquivo:</p>
        <p>{hash2}</p>
      </section>

      <form onSubmit={handleCompare}>
        <button type="submit">Comparar Hashes</button>
      </form>
      <section>
        <p>{comparisonResult}</p>
      </section>

      <h2>Buscar Dados Brutos</h2>
      <input type="text" placeholder="URL" onBlur={(e) => fetchRawData(e.target.value)} />
      <section>
        <p>Dados Brutos:</p>
        <p>{rawData}</p>
      </section>

      <h2>Enviar Requisição POST</h2>
      <input
        type="text"
        placeholder="URL"
        id="postUrl"
      />
      <textarea
        placeholder="Conteúdo JSON"
        id="postContent"
      ></textarea>
      <button
        onClick={() =>
          sendPostRequest(
            document.getElementById('postUrl').value,
            document.getElementById('postContent').value
          )
        }
      >
        Enviar
      </button>
      <section>
        <p>Resposta do POST:</p>
        <p>{postResponse}</p>
      </section>
    </main>
  );
}

export default App;
