const style = document.createElement('style');

style.appendChild(document.createTextNode(`
    .app-talk.in-call .top-bar.in-call,
    .local-media-controls,
    #localVideoContainer,
    button.stripe--collapse {
        display: none;
    }

    .stripe-wrapper {
        width: 100%;
    }
`));

document.getElementsByTagName('head')[0].appendChild(style);
