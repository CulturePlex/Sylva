var djangoUrls = {
    builder: "/reports/dh/builder",
    collabs: "/data/dh/collaborators/lookup/",
    del: "/reports/dh/delete",
    history: "/reports/dh/history",
    list: "/reports/dh/list",
    partials: "/reports/dh/partials",
    preview: "/reports/dh/pdf/preview",
    templates: "/reports/dh/templates"
}
var perms ={view: true, add: true, edit: true, del: true};
angular.module('reports').constant("REPORTS_PERMS", perms);
angular.module('reports').constant("DJANGO_URLS", djangoUrls);
angular.module('reports').constant("GRAPH", "dh");
angular.module('reports').constant("AS_MODAL", "");
