async function getDados(e) {
    e.preventDefault() // evita que a pagina de recarregar

    const icon = document.getElementById('loading-spinner');
    icon.style.display = 'block'; // mostra o spinner de carregamento

    const cep_aluno = document.getElementById('cep').value; // obtem o cep digitado no formulario
    const num_cep_aluno = document.getElementById('num_cep').value; // obtem o numero do imovel digitado no furmulario

    const url_api = `https://geolocation-api-ifpr.koyeb.app/car_data/${cep}/${num_cep}/ifpr%20-%20campus%20cascavel/85814-800/2020`; // url para consultar a API

    const dados_api = await fetch(url_api); // fazendo a requisição na API
    const data_api = await dados_api.json();// carregando o json da response

    // obtendo um array das coordenadas dos endereços
    const latlon_ini = data_api.coordenadas_inicio; //          lat         lon
    const latlon_fim = data_api.coordenadas_destino; //     Ex:[-24.916726, -53.41758]
        
    // url para consultar a API e criar um mapa interativo
    const url_map = `https://geolocation-api-ifpr.koyeb.app/rota?long_org=${latlon_ini[1]}&lat_org=${latlon_ini[0]}&long_dest=${latlon_fim[1]}&lat_dest=${latlon_fim[0]}`;

    //Se a consulta da API não retornar um CEP, um erro ocorre
    if (data_api.hasOwnProperty('erro')) {
        document.getElementById('cep').value = 'Endereço não encontrado!';    
    } else { // preenchendo o formulario html, com os dados retornados pela API
        document.getElementById('endereco_aluno').value = data_api.endereco_ini;
        document.getElementById('endereco_inst').value = data_api.endereco_instituicao;
        document.getElementById('distancia').value = (data_api.descricao_distancia);
        document.getElementById('temp_aprox').value = (data_api.duracao_minutos.toFixed(2)) + " min"; // deixando em minutos

        // Atualize o conteúdo do iframe com um mapa interativo, obtido pela API
        document.getElementById('iframe').style ="width: 1450px; height: 450px;";
        document.getElementById('iframe').src = url_map;
    } 
    icon.style.display = 'none';// Ocultar o spinner após o carregamento dos dados
}
// quando o input do numero do imovel perder o foco, ira chamar a function para obter os dados
document.getElementById('num_cep').addEventListener('focusout', getDados); 
