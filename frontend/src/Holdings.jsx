import { useEffect, useState } from "react";

const API_BASE_URL = (
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000"
).replace(/\/$/, "");


function Holdings() {

  const [holdings, setHoldings] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  const [showForm, setShowForm] =
    useState(false);

  const [editingId, setEditingId] =
    useState(null);

  const [form, setForm] = useState({
    symbol: "",
    quantity: "",
    buy_price: "",
    sector: "",
  });

  const [saving, setSaving] =
    useState(false);


  // =====================================================
  // GET HOLDINGS
  // =====================================================

  const fetchHoldings = async () => {

    try {

      setLoading(true);
      setError("");

      const token =
        localStorage.getItem(
          "access_token"
        );

      const response = await fetch(
        `${API_BASE_URL}/holdings`,
        {
          headers: {
            Authorization:
              `Bearer ${token}`,
          },
        }
      );

      if (response.status === 401) {

        throw new Error(
          "Session expired. Please login again."
        );
      }

      if (!response.ok) {

        throw new Error(
          "Failed to fetch holdings."
        );
      }

      const data =
        await response.json();

      setHoldings(data);

    } catch (error) {

      console.error(error);

      setError(
        error.message ||
        "Unable to load holdings."
      );

    } finally {

      setLoading(false);

    }
  };


  // =====================================================
  // INITIAL LOAD
  // =====================================================

  useEffect(() => {

    fetchHoldings();

  }, []);


  // =====================================================
  // FORM CHANGE
  // =====================================================

  const handleChange = (event) => {

    const {
      name,
      value,
    } = event.target;

    setForm(
      (previous) => ({
        ...previous,
        [name]: value,
      })
    );
  };


  // =====================================================
  // RESET FORM
  // =====================================================

  const resetForm = () => {

    setForm({
      symbol: "",
      quantity: "",
      buy_price: "",
      sector: "",
    });

    setEditingId(null);

    setShowForm(false);
  };


  // =====================================================
  // ADD HOLDING
  // =====================================================

  const handleAdd = () => {

    setForm({
      symbol: "",
      quantity: "",
      buy_price: "",
      sector: "",
    });

    setEditingId(null);

    setShowForm(true);
  };


  // =====================================================
  // EDIT HOLDING
  // =====================================================

  const handleEdit = (holding) => {

    setForm({
      symbol: holding.symbol,
      quantity: holding.quantity,
      buy_price: holding.buy_price,
      sector: holding.sector || "",
    });

    setEditingId(holding.id);

    setShowForm(true);
  };


  // =====================================================
  // SAVE HOLDING
  // =====================================================

  const handleSubmit = async (
    event
  ) => {

    event.preventDefault();

    try {

      setSaving(true);
      setError("");

      const token =
        localStorage.getItem(
          "access_token"
        );

      const payload = {

        symbol:
          form.symbol.trim(),

        quantity:
          Number(form.quantity),

        buy_price:
          Number(form.buy_price),

        sector:
          form.sector.trim() || null,
      };


      const url = editingId
        ? `${API_BASE_URL}/holdings/${editingId}`
        : `${API_BASE_URL}/holdings`;


      const method = editingId
        ? "PUT"
        : "POST";


      const response = await fetch(
        url,
        {
          method,

          headers: {
            "Content-Type":
              "application/json",

            Authorization:
              `Bearer ${token}`,
          },

          body:
            JSON.stringify(
              payload
            ),
        }
      );


      const data =
        await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Failed to save holding."
        );
      }


      await fetchHoldings();

      resetForm();

    } catch (error) {

      console.error(error);

      setError(
        error.message ||
        "Unable to save holding."
      );

    } finally {

      setSaving(false);

    }
  };


  // =====================================================
  // DELETE HOLDING
  // =====================================================

  const handleDelete = async (
    holdingId
  ) => {

    const confirmed =
      window.confirm(
        "Are you sure you want to delete this holding?"
      );

    if (!confirmed) {
      return;
    }


    try {

      setError("");

      const token =
        localStorage.getItem(
          "access_token"
        );


      const response =
        await fetch(
          `${API_BASE_URL}/holdings/${holdingId}`,
          {
            method: "DELETE",

            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );


      const data =
        await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Failed to delete holding."
        );
      }


      await fetchHoldings();

    } catch (error) {

      console.error(error);

      setError(
        error.message ||
        "Unable to delete holding."
      );
    }
  };


  // =====================================================
  // FORMAT CURRENCY
  // =====================================================

  const formatCurrency = (
    value
  ) => {

    return new Intl.NumberFormat(
      "en-IN",
      {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2,
      }
    ).format(
      Number(value) || 0
    );
  };


  // =====================================================
  // TOTAL INVESTED
  // =====================================================

  const totalInvested =
    holdings.reduce(
      (total, holding) =>
        total +
        Number(
          holding.invested_value || 0
        ),
      0
    );


  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {

    return (
      <section className="panel holdings-panel">

        <div className="panel-header">

          <h2>
            Portfolio Holdings
          </h2>

        </div>

        <p>
          Loading holdings...
        </p>

      </section>
    );
  }


  // =====================================================
  // UI
  // =====================================================

  return (

    <section className="panel holdings-panel">

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="panel-header">

        <div>

          <h2>
            Portfolio Holdings
          </h2>

          <span className="panel-subtitle">
            Manage your portfolio positions
          </span>

        </div>


        <button
          className="add-holding-button"
          onClick={handleAdd}
        >
          + Add Holding
        </button>

      </div>


      {/* =================================================
          ERROR
      ================================================= */}

      {error && (

        <div className="holdings-error">
          {error}
        </div>

      )}


      {/* =================================================
          TOTAL
      ================================================= */}

      <div className="holdings-summary">

        <div>

          <span>
            Total Invested
          </span>

          <strong>
            {formatCurrency(
              totalInvested
            )}
          </strong>

        </div>


        <div>

          <span>
            Holdings
          </span>

          <strong>
            {holdings.length}
          </strong>

        </div>

      </div>


      {/* =================================================
          ADD / EDIT FORM
      ================================================= */}

      {showForm && (

        <form
          className="holding-form"
          onSubmit={handleSubmit}
        >

          <div className="form-title">

            <h3>
              {editingId
                ? "Edit Holding"
                : "Add Holding"}
            </h3>

            <button
              type="button"
              onClick={resetForm}
              className="close-form-button"
            >
              ×
            </button>

          </div>


          <div className="holding-form-grid">

            <div className="holding-field">

              <label>
                Stock Symbol
              </label>

              <input
                type="text"
                name="symbol"
                value={form.symbol}
                onChange={handleChange}
                placeholder="e.g. RELIANCE.NS"
                required
              />

            </div>


            <div className="holding-field">

              <label>
                Quantity
              </label>

              <input
                type="number"
                name="quantity"
                value={form.quantity}
                onChange={handleChange}
                min="0.01"
                step="0.01"
                placeholder="Quantity"
                required
              />

            </div>


            <div className="holding-field">

              <label>
                Buy Price
              </label>

              <input
                type="number"
                name="buy_price"
                value={form.buy_price}
                onChange={handleChange}
                min="0.01"
                step="0.01"
                placeholder="Buy price"
                required
              />

            </div>


            <div className="holding-field">

              <label>
                Sector
              </label>

              <input
                type="text"
                name="sector"
                value={form.sector}
                onChange={handleChange}
                placeholder="e.g. Banking"
              />

            </div>

          </div>


          {/* =================================================
              AUTO VALUE PREVIEW
          ================================================= */}

          {form.quantity &&
            form.buy_price && (

            <div className="holding-value-preview">

              <span>
                Invested Value
              </span>

              <strong>
                {formatCurrency(
                  Number(
                    form.quantity
                  ) *
                  Number(
                    form.buy_price
                  )
                )}
              </strong>

            </div>

          )}


          <div className="holding-form-actions">

            <button
              type="button"
              onClick={resetForm}
              className="cancel-button"
            >
              Cancel
            </button>

            <button
              type="submit"
              className="save-holding-button"
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : editingId
                ? "Update Holding"
                : "Add Holding"}
            </button>

          </div>

        </form>

      )}


      {/* =================================================
          HOLDINGS TABLE
      ================================================= */}

      {holdings.length === 0 ? (

        <div className="empty-holdings">

          <div className="empty-icon">
            📊
          </div>

          <h3>
            No Holdings Yet
          </h3>

          <p>
            Add your first stock holding
            to start tracking your portfolio.
          </p>

        </div>

      ) : (

        <div className="holdings-table-wrapper">

          <table className="holdings-table">

            <thead>

              <tr>

                <th>
                  Stock
                </th>

                <th>
                  Sector
                </th>

                <th>
                  Quantity
                </th>

                <th>
                  Buy Price
                </th>

                <th>
                  Invested Value
                </th>

                <th>
                  Actions
                </th>

              </tr>

            </thead>


            <tbody>

              {holdings.map(
                (holding) => (

                  <tr
                    key={
                      holding.id
                    }
                  >

                    <td>

                      <strong>
                        {holding.symbol}
                      </strong>

                    </td>


                    <td>
                      {holding.sector ||
                        "-"}
                    </td>


                    <td>
                      {holding.quantity}
                    </td>


                    <td>
                      {formatCurrency(
                        holding.buy_price
                      )}
                    </td>


                    <td>

                      <strong>
                        {formatCurrency(
                          holding.invested_value
                        )}
                      </strong>

                    </td>


                    <td>

                      <div className="holding-actions">

                        <button
                          className="edit-holding-button"
                          onClick={() =>
                            handleEdit(
                              holding
                            )
                          }
                        >
                          Edit
                        </button>


                        <button
                          className="delete-holding-button"
                          onClick={() =>
                            handleDelete(
                              holding.id
                            )
                          }
                        >
                          Delete
                        </button>

                      </div>

                    </td>

                  </tr>

                )
              )}

            </tbody>

          </table>

        </div>

      )}

    </section>
  );
}


export default Holdings;