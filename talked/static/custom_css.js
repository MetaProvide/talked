const style = document.createElement("style");

style.appendChild(
    document.createTextNode(`
    .app-talk.in-call .top-bar.in-call,
    .local-media-controls,
    #localVideoContainer,
    button.stripe--collapse,
    .grid-navigation,
    .app-talk .vue-tooltip,
    .toastify,
    #app-navigation-vue {
        display: none;
    }

    #videos {
        height: 100% !important;
        top: 0 !important;
        padding: 8px !important;
    }

    .stripe-wrapper {
        width: 100% !important;
    }
`)
);

document.getElementsByTagName("head")[0].appendChild(style);
