//console.log(window.location.href)
let Http = new XMLHttpRequest()
let url = "localhost:7001"
data = "str data"//window.location.href
Http.open("POST", url, true)
Http.send(data)
