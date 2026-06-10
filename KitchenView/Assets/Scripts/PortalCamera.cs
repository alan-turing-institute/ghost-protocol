using UnityEngine;

[ExecuteAlways]
public class HeadTrackedPortalCamera : MonoBehaviour
{
    public Camera portalCamera;

    public Transform eye;

    // Physical TV corners in Unity/world coordinates.
    // These should describe the real TV rectangle.
    public Transform screenBottomLeft;
    public Transform screenBottomRight;
    public Transform screenTopLeft;

    public float nearClip = 0.01f;
    public float farClip = 100f;

    void LateUpdate()
    {
        if (!portalCamera || !eye ||
            !screenBottomLeft || !screenBottomRight || !screenTopLeft)
        {
            Debug.Log("Missing info");
            return;
        }

        Vector3 pa = screenBottomLeft.position;
        Vector3 pb = screenBottomRight.position;
        Vector3 pc = screenTopLeft.position;
        Vector3 pe = eye.position;

        Vector3 vr = (pb - pa).normalized;          // screen right
        Vector3 vu = (pc - pa).normalized;          // screen up
        Vector3 vn = Vector3.Cross(vr, vu).normalized; // screen normal

        // Make sure vn points toward the viewer.
        if (Vector3.Dot(vn, pa - pe) > 0)
        {
            vn = -vn;
        }

        Vector3 va = pa - pe;
        Vector3 vb = pb - pe;
        Vector3 vc = pc - pe;

        float d = -Vector3.Dot(va, vn);

        if (d <= 0.0001f)
        {
            return; // viewer is behind or too close to the screen plane
        }

        float l = Vector3.Dot(vr, va) * nearClip / d;
        float r = Vector3.Dot(vr, vb) * nearClip / d;
        float b = Vector3.Dot(vu, va) * nearClip / d;
        float t = Vector3.Dot(vu, vc) * nearClip / d;

        Matrix4x4 projection = PerspectiveOffCenter(l, r, b, t, nearClip, farClip);

        // Camera position is the tracked viewer.
        portalCamera.transform.position = pe;

        // Camera looks toward the screen.
        portalCamera.transform.rotation = Quaternion.LookRotation(-vn, vu);

        portalCamera.nearClipPlane = nearClip;
        portalCamera.farClipPlane = farClip;
        portalCamera.projectionMatrix = projection;
    }

    static Matrix4x4 PerspectiveOffCenter(
        float left,
        float right,
        float bottom,
        float top,
        float near,
        float far)
    {
        float x = 2.0f * near / (right - left);
        float y = 2.0f * near / (top - bottom);
        float a = (right + left) / (right - left);
        float b = (top + bottom) / (top - bottom);
        float c = -(far + near) / (far - near);
        float d = -(2.0f * far * near) / (far - near);
        float e = -1.0f;

        Matrix4x4 m = new Matrix4x4();

        m[0, 0] = x;
        m[0, 1] = 0;
        m[0, 2] = a;
        m[0, 3] = 0;

        m[1, 0] = 0;
        m[1, 1] = y;
        m[1, 2] = b;
        m[1, 3] = 0;

        m[2, 0] = 0;
        m[2, 1] = 0;
        m[2, 2] = c;
        m[2, 3] = d;

        m[3, 0] = 0;
        m[3, 1] = 0;
        m[3, 2] = e;
        m[3, 3] = 0;

        return m;
    }
}
