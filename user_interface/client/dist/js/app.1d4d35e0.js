(function(t){function e(e){for(var a,r,i=e[0],s=e[1],l=e[2],u=0,d=[];u<i.length;u++)r=i[u],Object.prototype.hasOwnProperty.call(o,r)&&o[r]&&d.push(o[r][0]),o[r]=0;for(a in s)Object.prototype.hasOwnProperty.call(s,a)&&(t[a]=s[a]);p&&p(e);while(d.length)d.shift()();return c.push.apply(c,l||[]),n()}function n(){for(var t,e=0;e<c.length;e++){for(var n=c[e],a=!0,r=1;r<n.length;r++){var i=n[r];0!==o[i]&&(a=!1)}a&&(c.splice(e--,1),t=s(s.s=n[0]))}return t}var a={},r={app:0},o={app:0},c=[];function i(t){return s.p+"js/"+({}[t]||t)+"."+{"chunk-6b0ef7ac":"6e642ea6","chunk-6fa0cb40":"c542ed7a","chunk-276649c9":"d2dae7c7","chunk-b514829a":"7dc61715","chunk-723cc955":"45aeeabf"}[t]+".js"}function s(e){if(a[e])return a[e].exports;var n=a[e]={i:e,l:!1,exports:{}};return t[e].call(n.exports,n,n.exports,s),n.l=!0,n.exports}s.e=function(t){var e=[],n={"chunk-6b0ef7ac":1,"chunk-6fa0cb40":1,"chunk-276649c9":1,"chunk-b514829a":1,"chunk-723cc955":1};r[t]?e.push(r[t]):0!==r[t]&&n[t]&&e.push(r[t]=new Promise((function(e,n){for(var a="css/"+({}[t]||t)+"."+{"chunk-6b0ef7ac":"fa5cdf09","chunk-6fa0cb40":"d9ec1c40","chunk-276649c9":"46ae5197","chunk-b514829a":"dcf98aeb","chunk-723cc955":"3861cd2c"}[t]+".css",o=s.p+a,c=document.getElementsByTagName("link"),i=0;i<c.length;i++){var l=c[i],u=l.getAttribute("data-href")||l.getAttribute("href");if("stylesheet"===l.rel&&(u===a||u===o))return e()}var d=document.getElementsByTagName("style");for(i=0;i<d.length;i++){l=d[i],u=l.getAttribute("data-href");if(u===a||u===o)return e()}var p=document.createElement("link");p.rel="stylesheet",p.type="text/css",p.onload=e,p.onerror=function(e){var a=e&&e.target&&e.target.src||o,c=new Error("Loading CSS chunk "+t+" failed.\n("+a+")");c.code="CSS_CHUNK_LOAD_FAILED",c.request=a,delete r[t],p.parentNode.removeChild(p),n(c)},p.href=o;var f=document.getElementsByTagName("head")[0];f.appendChild(p)})).then((function(){r[t]=0})));var a=o[t];if(0!==a)if(a)e.push(a[2]);else{var c=new Promise((function(e,n){a=o[t]=[e,n]}));e.push(a[2]=c);var l,u=document.createElement("script");u.charset="utf-8",u.timeout=120,s.nc&&u.setAttribute("nonce",s.nc),u.src=i(t);var d=new Error;l=function(e){u.onerror=u.onload=null,clearTimeout(p);var n=o[t];if(0!==n){if(n){var a=e&&("load"===e.type?"missing":e.type),r=e&&e.target&&e.target.src;d.message="Loading chunk "+t+" failed.\n("+a+": "+r+")",d.name="ChunkLoadError",d.type=a,d.request=r,n[1](d)}o[t]=void 0}};var p=setTimeout((function(){l({type:"timeout",target:u})}),12e4);u.onerror=u.onload=l,document.head.appendChild(u)}return Promise.all(e)},s.m=t,s.c=a,s.d=function(t,e,n){s.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:n})},s.r=function(t){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},s.t=function(t,e){if(1&e&&(t=s(t)),8&e)return t;if(4&e&&"object"===typeof t&&t&&t.__esModule)return t;var n=Object.create(null);if(s.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var a in t)s.d(n,a,function(e){return t[e]}.bind(null,a));return n},s.n=function(t){var e=t&&t.__esModule?function(){return t["default"]}:function(){return t};return s.d(e,"a",e),e},s.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},s.p="/",s.oe=function(t){throw console.error(t),t};var l=window["webpackJsonp"]=window["webpackJsonp"]||[],u=l.push.bind(l);l.push=e,l=l.slice();for(var d=0;d<l.length;d++)e(l[d]);var p=u;c.push([0,"chunk-vendors"]),n()})({0:function(t,e,n){t.exports=n("56d7")},"56d7":function(t,e,n){"use strict";n.r(e);n("e260"),n("e6cf"),n("cca6"),n("a79d");var a=n("2b0e"),r=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("v-app",[n("div",{attrs:{id:"app"}},[n("div",{attrs:{id:"modals"}}),n("NavBar",{on:{open_sidebar:function(e){t.sidebar_open=!t.sidebar_open}}},[n("router-view",{staticStyle:{height:"100vh","padding-top":"64px","padding-bottom":"64px"},attrs:{document_display_list:t.document_display_list,sidebar:t.sidebar_open},on:{update_doc_list:function(e){return t.updateDocList(t.list)}}})],1),n("v-footer",{attrs:{dark:"",padless:""}},[n("v-card",{staticClass:"lighten-1 white--text text-center",staticStyle:{height:"64px",position:"fixed",bottom:"0",width:"100%"},attrs:{flat:"",tile:""}},[n("v-card-text",{staticClass:"white--text"},[t._v(" "+t._s((new Date).getFullYear())+" — "),n("strong",[t._v("The Turing Institute")])])],1)],1)],1)])},o=[],c=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("v-card",{staticClass:"overflow-hidden"},[n("v-app-bar",{attrs:{absolute:"",color:"white","elevate-on-scroll":"","scroll-target":"#page"}},[n("v-row",{staticClass:"ma-0 pa-0",staticStyle:{"max-height":"100%",width:"100%","flex-grow":"1"},attrs:{justify:"left"}},[n("v-col",{staticClass:"ma-0 pa-0",staticStyle:{"max-width":"70px"},attrs:{cols:"1",align:"left"}},[n("v-app-bar-nav-icon",{class:{invisible:"Document"!=t.$route.name},on:{click:function(e){return t.$emit("open_sidebar")}}})],1),n("v-col",{staticClass:"ma-0 pa-2",staticStyle:{"max-width":"150px"},attrs:{cols:"2",align:"center"}},[n("v-btn",{attrs:{text:""}},[n("router-link",{staticStyle:{"text-decoration":"none",color:"inherit"},attrs:{to:{path:"/"}}},[t._v("Documents")])],1)],1),n("v-col",{staticClass:"ma-0 pa-2",staticStyle:{"max-width":"150px"},attrs:{cols:"2",align:"center"}},[n("v-btn",{attrs:{text:""}},[n("router-link",{staticStyle:{"text-decoration":"none",color:"inherit"},attrs:{to:{path:"/performance"}}},[t._v("Performance")])],1)],1),n("v-col",{staticClass:"ma-0 pa-1",attrs:{cols:"5",align:"center"}},[n("v-toolbar-title",[t._v("Elicit pre-alpha")])],1),n("v-col",{staticClass:"ma-0 pa-0",staticStyle:{"max-width":"70px"},attrs:{cols:"1",align:"right"}},[n("Export")],1)],1)],1),n("v-sheet",{staticClass:"overflow-y-auto",staticStyle:{height:"100vh"},attrs:{id:"page"}},[t._t("default")],2)],1)},i=[],s=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("v-btn",{attrs:{icon:""},on:{click:t.getData}},[n("v-icon",[t._v("mdi-content-save")])],1)},l=[],u=(n("d3b7"),n("3ca3"),n("ddb0"),n("2b3d"),n("9861"),n("bc3a")),d=n.n(u),p={methods:{getData:function(){var t="http://127.0.0.1:5000/api/get_data/";d.a.get(t).then((function(t){var e=window.URL.createObjectURL(new Blob([t.data])),n=document.createElement("a");n.href=e,n.setAttribute("download","export.csv"),document.body.appendChild(n),n.click()})).catch((function(t){console.error(t)}))},exportData:function(){this.$emit("export")}}},f=p,h=n("2877"),m=n("6544"),v=n.n(m),b=n("8336"),g=n("132d"),y=Object(h["a"])(f,s,l,!1,null,null,null),_=y.exports;v()(y,{VBtn:b["a"],VIcon:g["a"]});var w={components:{Export:_}},x=w,k=(n("e272"),n("40dc")),C=n("5bc1"),S=n("b0af"),j=n("62ad"),E=n("0fd9"),O=n("8dd9"),P=n("2a7f"),V=Object(h["a"])(x,c,i,!1,null,"1a3b8281",null),D=V.exports;v()(V,{VAppBar:k["a"],VAppBarNavIcon:C["a"],VBtn:b["a"],VCard:S["a"],VCol:j["a"],VRow:E["a"],VSheet:O["a"],VToolbarTitle:P["a"]});var T={name:"App",components:{NavBar:D},data:function(){return{sidebar_open:!1,document_display_list:[]}},methods:{updateDocList:function(t){this.document_display_list=t},getDocuments:function(){var t=this,e="http://127.0.0.1:5000/api/get_cases";d.a.get(e).then((function(e){t.document_display_list=e.data})).catch((function(t){console.error(t)}))}},mounted:function(){this.getDocuments()}},A=T,B=(n("d498"),n("7496")),L=n("99d9"),N=n("553a"),$=Object(h["a"])(A,r,o,!1,null,"c48fc226",null),I=$.exports;v()($,{VApp:B["a"],VCard:S["a"],VCardText:L["b"],VFooter:N["a"]});var M=n("f309");a["a"].use(M["a"]);var F=new M["a"]({}),R=n("8c4f");a["a"].use(R["a"]);var U=[{path:"/",name:"Home",component:function(){return Promise.all([n.e("chunk-6b0ef7ac"),n.e("chunk-6fa0cb40"),n.e("chunk-b514829a")]).then(n.bind(null,"7d97"))},props:!0},{path:"/doc/:id",name:"Document",component:function(){return Promise.all([n.e("chunk-6b0ef7ac"),n.e("chunk-723cc955")]).then(n.bind(null,"8b0d8"))},props:!0},{path:"/performance",name:"Performance",component:function(){return Promise.all([n.e("chunk-6b0ef7ac"),n.e("chunk-6fa0cb40"),n.e("chunk-276649c9")]).then(n.bind(null,"3e9c"))},props:!0}],q=new R["a"]({routes:U,mode:"history"}),H=q;n("f9e3");a["a"].config.productionTip=!1,new a["a"]({vuetify:F,router:H,render:function(t){return t(I)}}).$mount("#app")},c644:function(t,e,n){},d498:function(t,e,n){"use strict";n("c644")},e272:function(t,e,n){"use strict";n("f2b4")},f2b4:function(t,e,n){}});
//# sourceMappingURL=app.1d4d35e0.js.map