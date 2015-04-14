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

angular.module('reports').constant("DJANGO_URLS", djangoUrls);
angular.module('reports').constant("GRAPH", "dh")
