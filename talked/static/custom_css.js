const style = document.createElement("style");

style.appendChild(
    document.createTextNode(`
    .app-talk.in-call .top-bar.in-call,
    .local-media-controls,
    #localVideoContainer,
    button.stripe--collapse,
    .grid-navigation {
        display: none;
    }

    .stripe-wrapper {
        width: 100% !important;
    }
`)
);

document.getElementsByTagName("head")[0].appendChild(style);
