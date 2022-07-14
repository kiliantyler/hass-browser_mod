export const CameraMixin = (SuperClass) => {
  return class CameraMixinClass extends SuperClass {
    private _video;
    private _canvas;
    private _framerate;

    constructor() {
      super();
      this._framerate = 2;

      this._setup_camera();
    }

    async _setup_camera() {
      if (this._video) return;
      await this.connectionPromise;
      await this.firstInteraction;
      if (!this.cameraEnabled) return;

      const div = document.createElement("div");
      document.body.append(div);
      div.classList.add("browser-mod-camera");
      div.attachShadow({ mode: "open" });

      const styleEl = document.createElement("style");
      div.shadowRoot.append(styleEl);
      styleEl.innerHTML = `
      :host {
        display: none;
      }`;

      const video = (this._video = document.createElement("video"));
      div.shadowRoot.append(video);
      video.autoplay = true;
      video.playsInline = true;
      video.style.display = "none";

      const canvas = (this._canvas = document.createElement("canvas"));
      div.shadowRoot.append(canvas);
      canvas.style.display = "none";

      if (!navigator.mediaDevices) return;

      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });

      video.srcObject = stream;
      video.play();
      this.update_camera();
    }

    async update_camera() {
      if (!this.cameraEnabled) {
        const stream = this._video?.srcObject;
        if (stream) {
          stream.getTracks().forEach((t) => t.stop());
          this._video.scrObject = undefined;
        }
        return;
      }
      const video = this._video;
      const width = video.videoWidth;
      const height = video.videoHeight;
      this._canvas.width = width;
      this._canvas.height = height;
      const context = this._canvas.getContext("2d");
      context.drawImage(video, 0, 0, width, height);

      this.sendUpdate({
        camera: this._canvas.toDataURL("image/jpeg"),
      });

      const interval = Math.round(1000 / this._framerate);
      setTimeout(() => this.update_camera(), interval);
    }
  };
};
