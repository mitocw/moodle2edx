
fix_multichoice_images = function(){
    var apath = $('span.static_asset_path_dummy').find('a')[0].href;
    var static_path = apath.split('dummy.path')[0];
    console.log("[fix_multichoice_images] static_path=", static_path);
    $("label.response-label").each(function(idx, elem){
	var txt = elem.innerText;
	var m = txt.match(/^\!\[\]\(\/static\/(.*)\)$/);
	if (m){
	    var fp = m[1];
	    var new_fp = static_path + fp;
	    console.log("mapping ", txt, " to ", new_fp);
	    $(elem).find("text").html(String.fromCharCode(60) + "img src='" + new_fp + "'/" + String.fromCharCode(62));
	}
    });
}
fix_multichoice_images();
