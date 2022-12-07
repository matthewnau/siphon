//Check what script pieces to load.
$page=document.querySelector("title").textContent;
if ($page != "Siphon") {
	$section=document.querySelector("section");
	$overlay=document.getElementsByClassName("overlay")[0];
	$clipboard1 = new Clipboard('.copy2');
	$clipboard1.on('success', function() {alert("Copied!");});
	document.cookie="siphon_cookie_url=;expires=Thu, 01 Jan 1970 00:00:01 GMT;";
}

//All variables below.
$search=document.getElementsByClassName("search")[0];
$searchContainer=document.getElementsByClassName('search-container')[0];
$clearButton=document.getElementsByClassName('button')[1];
$sideBarToggle0=document.getElementsByClassName("sdbr")[0];
$sideBarToggle1=document.getElementsByClassName("sdbr")[1];
$sidebar_toggle = "off";
$sidebar=document.getElementsByClassName("sidebar")[0];
$lastScrollTop = 0;
$clipboard0 = new Clipboard('.copy1');

//All listeners below.
$search.onclick=function(){
	if ($page != "Siphon") {
		sidebar_off();
		focus_search();
		$overlay.classList.remove("hide");
	}
	else {
		sidebar_off();
		focus_search();
	}
};
$search.onblur=function(){
	if ($page != "Siphon") {
		sidebar_off();
		defocus_search();
		$overlay.classList.add("hide");
	}
	else {
		sidebar_off();
		defocus_search();
	}
};
$search.onkeyup=function(e){
	if ((e.keyCode == 13) && ($search.value != "") && ($page != "Siphon")) {
		siphon();
	}
	else if ((e.keyCode == 13) && ($search.value != "")) {
		document.getElementsById("indexForm").submit();
	}
}
$sideBarToggle0.onclick=function(){sidebar()};
$sideBarToggle1.onclick=function(){sidebar()};
$clipboard0.on('success', function() {alert("Copied!");});

//All functions below.
function siphon() {
	$url=$search.value;
	window.open('http://www.siphon.news/share/'+$url,"_self");
}

function focus_search() {
	$searchContainer.classList.add('focused','b');
	$clearButton.classList.remove('c3');
}

function defocus_search() {
	$searchContainer.classList.remove('focused','b','mt2','h6');
	$clearButton.classList.add('c3');
	$search.blur();
}

function sidebar(){
	if ($sidebar_toggle === "on") {
		sidebar_off();
	}
	else {
		sidebar_on();
	}
}

function sidebar_off(){
	$sidebar.classList.remove("l");
	$sidebar_toggle = "off";
}

function sidebar_on(){
	$sidebar.classList.add("l");
	$sidebar_toggle = "on";
}

function clear_input() {
	$search.value = "";
}

window.addEventListener("scroll", function(){  
	var st = window.pageYOffset || document.documentElement.scrollTop;  
	if (st > $lastScrollTop){
	   document.querySelector("nav").classList.add("scrolly--unpinned");
	   defocus_search();
	   sidebar_off();
	   $overlay.classList.add("hide");
	}
	else if (st === 0) {
	  document.querySelector("nav").classList.remove("scrolly--unpinned");
	}
	else {
	  document.querySelector("nav").classList.remove("scrolly--unpinned");
	}
	$lastScrollTop = st;
}, false);

function changeFontSize(size) {
	$section.style.fontSize=size.value+"px";
}

function changeFontFamily(font) {
	$section.style.fontFamily=font.value;
}
function resetSettings() {
	document.getElementsByClassName("fontForm")[0].value=20;
	$section.style.fontSize="20px";
	document.querySelectorAll("select")[0].selectedIndex=0;
	$section.style.fontFamily="Georgia";
	document.querySelectorAll("select")[1].selectedIndex=0;
}
function drawer(group,num) {
	$temp=document.getElementById(group);
	$w2=document.getElementsByClassName("chev"+num.toString())[0];
	if ($temp.classList.contains("hide")) {
		$temp.classList.remove("hide");
		$w2.style.transform="rotate(0deg)";
	}
	else {
		$temp.classList.add("hide");
		$w2.style.transform="rotate(180deg)";
	}
}