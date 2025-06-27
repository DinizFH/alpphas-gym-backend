// src/pages/PlanosAlimentares/ModalConfirmarExclusao.jsx

import React from "react";

export default function ModalConfirmarExclusao({ onClose, onConfirm, nomePlano }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded shadow-md max-w-md w-full">
        <h2 className="text-xl font-semibold mb-4 text-red-600">
          Confirmar exclusão
        </h2>
        <p className="mb-6">
          Tem certeza que deseja excluir o plano{" "}
          <strong>{nomePlano}</strong>? Esta ação não poderá ser desfeita.
        </p>

        <div className="flex justify-end gap-4">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
          >
            Cancelar
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Confirmar Exclusão
          </button>
        </div>
      </div>
    </div>
  );
}
