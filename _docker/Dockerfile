FROM johnnysmitherson/crack-dev:base

# Install Blender 5.1.2 dependencies + xvfb for headless GUI
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    imagemagick \
    xvfb \
    libgl1-mesa-glx \
    libxi6 \
    libxrender1 \
    libxxf86vm1 \
    && rm -rf /var/lib/apt/lists/*

# Download and install Blender 5.1.2
ARG BLENDER_VERSION=5.1.2
ARG BLENDER_SHA256=aaccb355f50183979b698bcce7467103a76261b5fa59f4972295842662a285fb
ARG BLENDER_URL=https://download.blender.org/release/Blender5.1/blender-5.1.2-linux-x64.tar.xz

RUN cd /opt \
    && wget -q "${BLENDER_URL}" -O blender.tar.xz \
    && echo "${BLENDER_SHA256}  blender.tar.xz" | sha256sum -c - \
    && tar -xf blender.tar.xz \
    && mv blender-${BLENDER_VERSION}-linux-x64 blender-${BLENDER_VERSION} \
    && ln -sf /opt/blender-${BLENDER_VERSION}/blender /usr/local/bin/blender \
    && rm blender.tar.xz

# Install blender-mcp (provides MCP server CLI + addon.py)
# Use --break-system-packages since container is isolated
RUN pip install --no-cache-dir --break-system-packages blender-mcp==1.6.4

# Install blender-mcp addon for Blender 5.1
# The addon module must be named 'blendermcp.py' to match bl_info["name"] = "Blender MCP"
RUN BLENDER_ADDON_DIR="/root/.config/blender/5.1/scripts/addons" \
    && mkdir -p "${BLENDER_ADDON_DIR}" \
    && python3 -c "import blender_mcp; import os; print(os.path.dirname(blender_mcp.__file__))" | xargs -I{} cp {}/addon.py "${BLENDER_ADDON_DIR}/blendermcp.py"

VOLUME /root
WORKDIR /workspace

EXPOSE 22 9877

CMD ["/usr/sbin/sshd", "-D"]