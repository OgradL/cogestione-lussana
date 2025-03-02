
async function send_comando() {
    let input = document.getElementById("comando");
	console.log(input.value);
	let comando = input.value;
	console.log(document.URL);
	const response = await fetch(document.URL, {
		method:"POST",
		headers:
			{"comando" : comando}
	});

	console.log(await response.headers)
	// console.log(await response.text())

	document.getElementById("result").innerText = await response.headers.get("result");

}