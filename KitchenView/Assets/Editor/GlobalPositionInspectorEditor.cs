using UnityEditor;
using UnityEngine;

[CustomEditor(typeof(GlobalPositionInspector))]
[CanEditMultipleObjects]
public class GlobalPositionInspectorEditor : Editor
{
    private SerializedProperty _targetOverride;

    private void OnEnable()
    {
        _targetOverride = serializedObject.FindProperty(nameof(GlobalPositionInspector.targetOverride));
    }

    public override void OnInspectorGUI()
    {
        serializedObject.Update();

        EditorGUILayout.PropertyField(_targetOverride, new GUIContent("Target Transform"));
        serializedObject.ApplyModifiedProperties();

        EditorGUILayout.Space(8f);

        if (targets.Length > 1)
        {
            DrawMultipleTargetReadout();
            return;
        }

        DrawSingleTargetInspector((GlobalPositionInspector)target);
    }

    public override bool RequiresConstantRepaint()
    {
        return true;
    }

    private static void DrawSingleTargetInspector(GlobalPositionInspector inspector)
    {
        Transform targetTransform = inspector.TargetTransform;

        if (targetTransform == null)
        {
            EditorGUILayout.HelpBox("No Transform is available to inspect.", MessageType.Warning);
            return;
        }

        EditorGUILayout.LabelField("World Space", EditorStyles.boldLabel);

        EditorGUI.BeginChangeCheck();
        Vector3 newPosition = EditorGUILayout.Vector3Field("Global Position", targetTransform.position);

        if (EditorGUI.EndChangeCheck())
        {
            Undo.RecordObject(targetTransform, "Set Global Position");
            targetTransform.position = newPosition;
            EditorUtility.SetDirty(targetTransform);
        }

        using (new EditorGUI.DisabledScope(true))
        {
            EditorGUILayout.Vector3Field("Local Position", targetTransform.localPosition);
            EditorGUILayout.Vector3Field("Global Rotation", targetTransform.eulerAngles);
        }

        EditorGUILayout.Space(6f);
        DrawCopyButtons(targetTransform.position);
    }

    private static void DrawMultipleTargetReadout()
    {
        EditorGUILayout.LabelField("World Space", EditorStyles.boldLabel);
        EditorGUILayout.HelpBox("Select one Global Position Inspector to edit or copy its exact position.", MessageType.Info);
    }

    private static void DrawCopyButtons(Vector3 position)
    {
        using (new EditorGUILayout.HorizontalScope())
        {
            if (GUILayout.Button("Copy XYZ"))
            {
                CopyToClipboard($"{position.x:F6}, {position.y:F6}, {position.z:F6}");
            }

            if (GUILayout.Button("Copy Vector3"))
            {
                CopyToClipboard($"new Vector3({position.x:F6}f, {position.y:F6}f, {position.z:F6}f)");
            }
        }
    }

    private static void CopyToClipboard(string text)
    {
        EditorGUIUtility.systemCopyBuffer = text;
        Debug.Log($"Copied global position: {text}");
    }
}
