openerp.npp_session_timeout = function(instance){
    var _t = instance.web._t;
    var QWeb = instance.web.qweb

    instance.web.CrashManager.include({
         show_warning: function(error) {
              if (!this.active || $('#session_expired').length) {
                  return;
              }
              if (error.data.exception_type === "except_osv") {
                  error = _.extend({}, error, {data: _.extend({}, error.data, {message: error.data.arguments[0] + "\n\n" + error.data.arguments[1]})});
              }
              var id_session_expired = ''
              if (error.type === "Session Expired") {
                   id_session_expired = 'id="session_expired"'
              }
              new instance.web.Dialog(this, {
                  size: 'medium',
                  title: "Nippon " + (_.str.capitalize(error.type) || "Warning"),
                  buttons: [
                      {text: _t("Ok"), click: function() { this.parents('.modal').modal('hide'); }}
                  ],
              }, $('<div '+id_session_expired+'>' + QWeb.render('CrashManager.warning', {error: error}) + '</div>')).open();
        },
    });
}