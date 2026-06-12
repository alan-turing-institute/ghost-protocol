using UnityEngine;

/// <summary>
/// Attach this to any GameObject to view or edit a Transform's world position
/// from a custom inspector.
/// </summary>
[ExecuteAlways]
[AddComponentMenu("Tools/Global Position Inspector")]
public class GlobalPositionInspector : MonoBehaviour
{
    [Tooltip("Optional Transform to inspect. If empty, this GameObject's Transform is used.")]
    public Transform targetOverride;

    public Transform TargetTransform => targetOverride != null ? targetOverride : transform;

    public Vector3 GlobalPosition => TargetTransform != null ? TargetTransform.position : Vector3.zero;
}
