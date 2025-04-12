
async function send_comando() {
    let input = document.getElementById("comando");
	console.log(input.value);
	let comando = input.value;
	// console.log(document.URL);
	const response = await fetch(document.URL, {
		method:"POST",
		body: JSON.stringify({"comando" : comando})
	});

	console.log(await response.headers)
	// console.log(await response.text())
	body = await response.json();

	console.log(body.res);

	// document.getElementById("result").innerText = await response.headers.get("result");
	document.getElementById("result").innerText = body.res;

}

async function iscrizione(corso_id) {
	let url = "/iscrizione/";
	// console.log(document.URL, url);
	await fetch(url, {
		method: "POST",
		body: JSON.stringify({id_corso : corso_id})
	}).then((res) => {
		window.location.reload();
	});

	// console.log(response.status);
}

async function annulla_iscrizione(corso_id) {
	let url = "/annulla-iscrizione/";

	await fetch(url, {
		method: "POST",
		body: JSON.stringify({id_corso : corso_id})
	}).then((ret) => {
		window.location.reload();
	});
}

function del_flashed_message(message) {
	message.parentElement.remove();
}

function segna_presenza(id_user, presenza){
	prebut = document.getElementById("pres-" + id_user);
	assbut = document.getElementById("asse-" + id_user);

	if (presenza == 1){
		assbut.classList.remove("app-gray");
		assbut.classList.remove("app-red");
		assbut.classList.add("app-gray");

		prebut.classList.remove("app-gray");
		prebut.classList.remove("app-green");
		prebut.classList.add("app-green");
	} else {
		assbut.classList.remove("app-gray");
		assbut.classList.remove("app-red");
		assbut.classList.add("app-red");

		prebut.classList.remove("app-gray");
		prebut.classList.remove("app-green");
		prebut.classList.add("app-gray");
	}
}

async function salva_presenze(){
	tabella = document.getElementById("lista-appello").children[0];

	result = new Map();

	for (var i = 0; i < tabella.children.length; i++){
		var child = tabella.children[i];

		if (child.id == "ids")
			continue;

		id_user = child.id.substring(4);

		prebut = document.getElementById("pres-" + id_user);
		assbut = document.getElementById("asse-" + id_user);

		if (prebut.classList.contains("app-green")){
			result.set(id_user, true);
		} else if (assbut.classList.contains("app-red")){
			result.set(id_user, false);
		}
	}

	objRes = Object.fromEntries(result);

	let url = window.location.href;
	console.log(url);

	await fetch(url, {
		method: "POST",
		body: JSON.stringify(objRes)
	}).then((ret) => {
		window.location.reload();
	});
}