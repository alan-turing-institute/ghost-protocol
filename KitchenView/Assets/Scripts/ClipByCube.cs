using UnityEngine;

public class ClipByCube : MonoBehaviour
{
    public Transform clippingCube;

    private Renderer rend;

    void Start()
    {
        rend = GetComponent<Renderer>();
    }

    void Update()
    {
        if (clippingCube == null || rend == null)
            return;

        // Converts world-space positions into the cube's local space
        rend.material.SetMatrix("_CubeWorldToLocal", clippingCube.worldToLocalMatrix);
    }
}
