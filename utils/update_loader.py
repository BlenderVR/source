import sys
import os

input  = sys.argv[(sys.argv.index('--')+1)]
output = input.split('.')
output.insert(-1, 'vr')
output = '.'.join(output)
if not sys.platform.startswith('win'):
    output = os.path.join(os.path.dirname(output), '.' + os.path.basename(output))

try:
    import bpy
    in_blender = True
except:
    in_blender = False

if in_blender:

    bpy.ops.wm.open_mainfile(filepath=input)

    camera = None
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            camera = obj
            break

    if camera:
        SENSOR='Always_for_blenderVR'
        bpy.ops.logic.sensor_add(type='ALWAYS', name=SENSOR, object=camera.name)
        sensor = camera.game.sensors.get(SENSOR)
        sensor.use_pulse_true_level = True

        CONTROLLER = 'Controller_for_blenderVR'
        bpy.ops.logic.controller_add(type='PYTHON', name=CONTROLLER, object=camera.name)
        controller = camera.game.controllers.get(CONTROLLER)
        controller.mode = 'MODULE'
        controller.module = 'blendervr.run'

        ACTUATOR = 'Occulus_filter_for_blenderVR'
        bpy.ops.logic.actuator_add(type='FILTER_2D', name=ACTUATOR, object=camera.name)
        actuator = camera.game.actuators.get(ACTUATOR)
        actuator.mode = 'CUSTOMFILTER'

        TEXT = 'Occulus_glsl_for_blenderVR'
        shader = bpy.data.texts.new(TEXT)
        actuator.glsl_shader = shader
        shader.from_string("""uniform sampler2D bgl_RenderedTexture;

    const vec4 kappa = vec4(1.0,1.7,0.7,15.0);

    uniform float screen_width;
    uniform float screen_height;

    const float scaleFactor = 0.9;

    const vec2 leftCenter = vec2(0.25, 0.5);
    const vec2 rightCenter = vec2(0.75, 0.5);

    // Scales input texture coordinates for distortion.
    vec2 hmdWarp(vec2 LensCenter, vec2 texCoord, vec2 Scale, vec2 ScaleIn) {
        vec2 theta = (texCoord - LensCenter) * ScaleIn; 
        float rSq = theta.x * theta.x + theta.y * theta.y;
        vec2 rvector = theta * (kappa.x + kappa.y * rSq + kappa.z * rSq * rSq + kappa.w * rSq * rSq * rSq);
        vec2 tc = LensCenter + Scale * rvector;
        return tc;
    }

    bool validate(vec2 tc, int left_eye) {
        //keep within bounds of texture 
        if ((left_eye == 1 && (tc.x < 0.0 || tc.x > 0.5)) ||   
            (left_eye == 0 && (tc.x < 0.5 || tc.x > 1.0)) ||
            tc.y < 0.0 || tc.y > 1.0) {
            return false;
        }
        return true;
    }

    void main() {
        vec2 screen = vec2(screen_width, screen_height);

        float as = float(screen.x / 2.0) / float(screen.y);
        vec2 Scale = vec2(0.5, as);
        vec2 ScaleIn = vec2(2.0 * scaleFactor, 1.0 / as * scaleFactor);

        vec2 texCoord = gl_TexCoord[0].st;

        vec2 tc = vec2(0);
        vec4 color = vec4(0);

        if (texCoord.x < 0.5) {
            tc = hmdWarp(leftCenter, texCoord, Scale, ScaleIn );
            color = texture2D(bgl_RenderedTexture, tc);
            if (!validate(tc, 1))
                color = vec4(0);
        } else {
            tc = hmdWarp(rightCenter, texCoord, Scale, ScaleIn);
            color = texture2D(bgl_RenderedTexture, tc);
            if (!validate(tc, 0))
                color = vec4(0);
        }   
        gl_FragColor = color;
    }    
    """)

        controller.link(sensor=sensor)
        controller.link(actuator=actuator)

    bpy.ops.wm.save_as_mainfile(copy=True, filepath=output, relative_remap=True)

else:

    print(output)
