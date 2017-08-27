var system = require('system');
var page = require('webpage').create();
var fs = require('fs');

page.viewportSize = {
  width: 1300,
  height: 800
}

page.open((system.args[1] +"-"+ system.args[2] +".html"), function()
{
  //console.log(system.args[1]);
  //console.log(system.args[2]);
  window.setTimeout(function(){
    var base64Data = page.evaluate(function(s){
      var r = document.querySelector(s).toDataURL("image/png").split(",")[1];
      return r;
    }, '#canvas canvas');
    //console.log(base64Data);
    
    var now = new Date();
    //console.log(now);
    var filename = system.args[2] +"/"+ system.args[2] +"-"+ now.getFullYear() +"-"+ (now.getMonth()+1) +"-"+ now.getDate() +"-"+ now.getHours() +":";
    if(now.getMinutes() < 10){
      filename += "0";
    }
    filename += now.getMinutes() +":"+ now.getSeconds() +".png";
    //console.log(filename);


    
    fs.write(filename, atob(base64Data), 'wb');
    
    phantom.exit();
  }, 5000);
});

phantom.onError = function(msg, trace) {
  var msgStack = ['PHANTOM ERROR: ' + msg];
  if (trace && trace.length) {
    msgStack.push('TRACE:');
    trace.forEach(function(t) {
      msgStack.push(' -> ' + (t.file || t.sourceURL) + ': ' + t.line + (t.function ? ' (in function ' + t.function +')' : ''));
    });
  }
  console.error(msgStack.join('\n'));
  phantom.exit(1);
};
